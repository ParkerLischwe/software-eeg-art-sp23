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
scale = BUFFER_SIZE/256
num_samples_processed = 0
num_fft_calc = 0
sample_factor = 1
sample_counter = 0

# counter variable controls the sliding window granularity (this is initialized one less than the amount of new points you wait for to make next fft calc)
counter = 29

TP9_buff = CircularBuffer(BUFFER_SIZE)
oldest_idxTP9 = 0
newest_idxTP9 = 0

AF7_buff = CircularBuffer(BUFFER_SIZE)
oldest_idxAF7 = 0
newest_idxAF7 = 0

AF8_buff = CircularBuffer(BUFFER_SIZE)
oldest_idxAF8 = 0
newest_idxAF8 = 0

TP10_buff = CircularBuffer(BUFFER_SIZE)
oldest_idxTP10 = 0
newest_idxTP10 = 0



# Define a callback function to handle incoming OSC messages
def process_eeg_signal(address, *args):
    global num_samples_processed, sample_factor, counter, sample_counter, num_fft_calc
    global TP9_buff, AF7_buff, AF8_buff, TP10_buff
    global oldest_idxTP9, newest_idxTP9, oldest_idxAF7, newest_idxAF7
    global oldest_idxAF8, newest_idxAF8, oldest_idxTP10, newest_idxTP10
    sample_id = args[0]
    unix_ts = args[1] + args[2]
    lsl_ts = args[3] + args[4]
    data = args[5:]

    # This chunk controls how much data we sample from the incoming stream. 
    # When equal to 1 we sample every data point in the stream
    #Does this work? See if tuning this changes anything
    sample_counter += 10
    if counter % sample_factor != 0:
        return

     # Add new samples to channel 1 buffer
    TP9_buff.add_sample(data[0])
    newest_idxTP9 += 1

    # Add new samples to channel 2 buffer
    AF7_buff.add_sample(data[1])
    newest_idxAF7 += 1
    
    # Add new samples to channel 3 buffer
    AF8_buff.add_sample(data[2])
    newest_idxAF8 += 1
    
    # Add new samples to channel 4 buffer
    TP10_buff.add_sample(data[3])
    newest_idxTP10 += 1 
    
    if num_samples_processed >= BUFFER_SIZE:
        counter += 1
        if counter == 30:
            counter = 0
            # print(ch1_buff.size)
            TP9_fft = np.fft.fft(TP9_buff.buffer)
            TP9_gamma = np.sum(np.abs(TP9_fft[int((30*scale)):int((100*scale))]))
            TP9_beta = np.sum(np.abs(TP9_fft[int((12*scale)):int((30*scale))]))
            TP9_alpha = np.sum(np.abs(TP9_fft[int((8*scale)):int((12*scale))]))
            TP9_theta = np.sum(np.abs(TP9_fft[int((4*scale)):int((8*scale))]))

            # Process ch2 data
            AF7_fft = np.fft.fft(AF7_buff.buffer)
            AF7_gamma = np.sum(np.abs(AF7_fft[int((30*scale)):int((100*scale))]))
            AF7_beta = np.sum(np.abs(AF7_fft[int((12*scale)):int((30*scale))]))
            AF7_alpha = np.sum(np.abs(AF7_fft[int((8*scale)):int((12*scale))]))
            AF7_theta = np.sum(np.abs(AF7_fft[int((4*scale)):int((8*scale))]))

            # Process ch3 data
            AF8_fft = np.fft.fft(AF8_buff.buffer)
            AF8_gamma = np.sum(np.abs(AF8_fft[int((30*scale)):int((100*scale))]))
            AF8_beta = np.sum(np.abs(AF8_fft[int((12*scale)):int((30*scale))]))
            AF8_alpha = np.sum(np.abs(AF8_fft[int((8*scale)):int((12*scale))]))
            AF8_theta = np.sum(np.abs(AF8_fft[int((4*scale)):int((8*scale))]))

            # Process ch4 data
            TP10_fft = np.fft.fft(TP10_buff.buffer)
            TP10_gamma = np.sum(np.abs(TP10_fft[int((30*scale)):int((100*scale))]))
            TP10_beta = np.sum(np.abs(TP10_fft[int((12*scale)):int((30*scale))]))
            TP10_alpha = np.sum(np.abs(TP10_fft[int((8*scale)):int((12*scale))]))
            TP10_theta = np.sum(np.abs(TP10_fft[int((4*scale)):int((8*scale))]))

            # Calculate x and y coordinates of the mouse coordinates
            # x is calculated using the lateralization index on theta bands from TP9(left hem) and TP10(right hem) channels
            # y is calculated using the lateralizaation index on alpha bands from TP9(left hem) and TP10(right hem) channels
            # If x or y is pos, more power in right hem which indicates (high and to the right is high right brain activity)
            x_coord = (TP10_theta - TP9_theta)/(TP10_theta + TP9_theta)
            y_coord = (TP10_alpha - TP9_alpha)/(TP10_alpha + TP9_alpha) 

            # Reset oldest indices for all buffers
            oldest_idxTP9 = newest_idxTP9 - BUFFER_SIZE
            oldest_idxAF7 = newest_idxAF7 - BUFFER_SIZE
            oldest_idxAF8 = newest_idxAF8 - BUFFER_SIZE
            oldest_idxTP10 = newest_idxTP10 - BUFFER_SIZE

            # Wrap around if we've reached the end of the buffer
            if oldest_idxTP9 < 0:
                oldest_idxTP9 += BUFFER_SIZE
            if oldest_idxAF7 < 0:
                oldest_idxAF7 += BUFFER_SIZE
            if oldest_idxAF8 < 0:
                oldest_idxAF8 += BUFFER_SIZE
            if oldest_idxTP10 < 0:
                oldest_idxTP10 += BUFFER_SIZE

            data = [x_coord, y_coord]
            client = SimpleUDPClient('127.0.0.1', 5005)
            client.send_message('/PetalStream/eeg', data)
            print("Data is here: ", data)

    num_samples_processed += 1

    
    # print("Data is here: ", data)
    # client.send_message('/PetalStream/eeg', data)
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
