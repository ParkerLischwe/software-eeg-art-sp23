from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import numpy as np
import queue
import threading

# Create callback function so we know max got the message
def it_got_to_max(address, *args):
    print("Max data recieved: ", args)

# Create a dispatcher and register the callback function
dispatcher_max = Dispatcher()
dispatcher_max.map("/PetalStream/eeg", it_got_to_max)

# Create a server that represents the port max will use and start listening for incoming OSC messages
server_address_max = ("127.0.0.1", 5006)
server_max = BlockingOSCUDPServer(server_address_max, dispatcher_max)

# Define the circular buffer class
# class CircularBuffer:
#     def __init__(self, size):
#         self.buffer = np.zeros(size)
#         self.size = size
#         self.index = 0

#     def add_sample(self, sample):
#         self.buffer[self.index] = sample
#         self.index = (self.index + 1) % self.size

#     def get_samples(self):
#         return self.buffer
class CircularBuffer:
    def __init__(self, size):
        self.buffer = np.zeros(size)
        self.size = size
        self.index = 0

    def add_sample(self, sample):
        self.buffer[self.index] = sample
        self.index = (self.index + 1) % self.size

    def get_samples(self):
        return self.buffer

BUFFER_SIZE = 512
num_samples_processed = 0
sample_factor = 1
sample_counter = 0

# counter variable controls the sliding window granularity (5 waits for 5 points to make next fft calculation)
counter = 0

ch1_buff = CircularBuffer(BUFFER_SIZE)
oldest_idx1 = 0
newest_idx1 = 0

ch2_buff = CircularBuffer(BUFFER_SIZE)
oldest_idx2 = 0
newest_idx2 = 0

ch3_buff = CircularBuffer(BUFFER_SIZE)
oldest_idx3 = 0
newest_idx3 = 0

ch4_buff = CircularBuffer(BUFFER_SIZE)
oldest_idx4 = 0
newest_idx4 = 0



# Define a callback function to handle incoming OSC messages
def process_eeg_signal(address, *args):
    global num_samples_processed, sample_factor, counter, sample_counter
    global ch1_buff, ch2_buff, ch3_buff, ch4_buff
    global oldest_idx1, newest_idx1, oldest_idx2, newest_idx2
    global oldest_idx3, newest_idx3, oldest_idx4, newest_idx4
    sample_id = args[0]
    unix_ts = args[1] + args[2]
    lsl_ts = args[3] + args[4]
    data = args[5:]

    # This chunk controls how much data we sample from the incoming stream. 
    # When equal to 1 we sample every data point in the stream
    sample_counter += 1
    if counter % sample_factor != 0:
        return

     # Add new samples to channel 1 buffer
    ch1_buff.add_sample(data[0])
    newest_idx1 += 1

    # Add new samples to channel 2 buffer
    ch2_buff.add_sample(data[1])
    newest_idx2 += 1
    
    # Add new samples to channel 3 buffer
    ch3_buff.add_sample(data[2])
    newest_idx3 += 1
    
    # Add new samples to channel 4 buffer
    ch4_buff.add_sample(data[3])
    newest_idx4 += 1
    
    counter += 1
    
    if counter == 3:
        counter = 0
        try:
            
        # Process ch1 data
        print(ch1_buff.size)
        channel1_fft = np.fft.fft(ch1_buff)[:256]
        ch1_gamma = np.sum(np.abs(channel1_fft[32:100]))
        ch1_beta = np.sum(np.abs(channel1_fft[13:32]))
        ch1_alpha = np.sum(np.abs(channel1_fft[4:8]))
        ch1_theta = np.sum(np.abs(channel1_fft[0:4]))

        # Process ch2 data
        channel2_fft = np.fft.fft(ch2_buff)[:256]
        ch2_gamma = np.sum(np.abs(channel2_fft[32:100]))
        ch2_beta = np.sum(np.abs(channel2_fft[13:32]))
        ch2_alpha = np.sum(np.abs(channel2_fft[4:8]))
        ch2_theta = np.sum(np.abs(channel2_fft[0:4]))

        # Process ch3 data
        channel3_fft = np.fft.fft(ch3_buff)[:256]
        ch3_gamma = np.sum(np.abs(channel3_fft[32:100]))
        ch3_beta = np.sum(np.abs(channel3_fft[13:32]))
        ch3_alpha = np.sum(np.abs(channel3_fft[4:8]))
        ch3_theta = np.sum(np.abs(channel3_fft[0:4]))

        # Process ch4 data
        channel4_fft = np.fft.fft(ch4_buff)[:256]
        ch4_gamma = np.sum(np.abs(channel4_fft[32:100]))
        ch4_beta = np.sum(np.abs(channel4_fft[13:32]))
        ch4_alpha = np.sum(np.abs(channel4_fft[4:8]))
        ch4_theta = np.sum(np.abs(channel4_fft[0:4]))

        # Reset oldest indices for all buffers
        oldest_idx1 = newest_idx1 - BUFFER_SIZE
        oldest_idx2 = newest_idx2 - BUFFER_SIZE
        oldest_idx3 = newest_idx3 - BUFFER_SIZE
        oldest_idx4 = newest_idx4 - BUFFER_SIZE

        # Wrap around if we've reached the end of the buffer
        if oldest_idx1 < 0:
            oldest_idx1 += BUFFER_SIZE
        if oldest_idx2 < 0:
            oldest_idx2 += BUFFER_SIZE
        if oldest_idx3 < 0:
            oldest_idx3 += BUFFER_SIZE
        if oldest_idx4 < 0:
            oldest_idx4 += BUFFER_SIZE
        data = [ch1_gamma, ch2_gamma, ch3_gamma, ch4_gamma]

    num_samples_processed += 1

    client = SimpleUDPClient('127.0.0.1', 5005)
    print("Data is here: ", data)
    client.send_message('/PetalStream/eeg', data)
    # server_max.handle_request()
    # server_max.serve_forever()
    # print(f"max Received OSC message: {address} {args}")

# Create a dispatcher object and register the callback function with it
dispatcher = Dispatcher()
dispatcher.map("/PetalStream/eeg", process_eeg_signal)

# Create a server object and start listening for OSC messages
server_address = ('localhost', 1337)
server = BlockingOSCUDPServer(server_address, dispatcher)
print(f"Listening for OSC messages on {server_address[0]}:{server_address[1]}...")
server.serve_forever()
