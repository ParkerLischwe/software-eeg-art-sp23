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

center_attr = 0.1
#How fast we want to change the attraction levels
attraction_cntr = 0
bt_ratio = 0
min_value_bt = 0
max_value_bt = 0
max_value_cent = 0
min_value_cent = 0
bt_final = 0
center_attr_final = 1
prev_cent_attr = 0
prev_bt_final = 0
first_bt = True
first_centr = True
#How fast we want to change the coordinates
coord_cnt = 0
x_coord = 0
y_coord = 0


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
    global num_samples_processed, sample_factor, counter, sample_counter, num_fft_calc, attraction_cntr, center_attr, bt_ratio, center_attr_final, coord_cnt, x_coord, y_coord
    global TP9_buff, AF7_buff, AF8_buff, TP10_buff, min_value_bt, max_value_bt, bt_final, prev_cent_attr, prev_bt_final, max_value_cent, min_value_cent, first_centr, first_bt
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
            attraction_cntr += 1
            coord_cnt += 1
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
            if coord_cnt == 2:
                x_coord = (TP10_theta - TP9_theta)/(TP10_theta + TP9_theta)
                y_coord = (TP10_alpha - TP9_alpha)/(TP10_alpha + TP9_alpha)
                # print("coords: ", x_coord, y_coord)
                coord_cnt = 0

            # Calculate center attraction coefficient, which ranges from 0 to 1
            # We use alpha synchronization because of its relation to creativity. Higher right hemisphere activity is associated with higher levels of creativity
            # Use AF7 and AF8 channels for this (frontal regions are usually expressed more in this domain - i think)
            # If value is more positive, there is more left hemispheric activity, which means lower levels of creativity and therefore higher center attraction force (higher force = less of a flow state that would represent creative thinking)
            # Normalize center attraction from range(-1, 1) to range(0.01, 0.4) which to me has most interesting attraction range
            # This variable should be getting updated less often than the  and y coordinates, mess around with this update
            # bt_ration is beta/theta which means that when this ratio is large, there is more focus and therefore larger attraction because it is less of a flow state (lower beta/theta means greater flow state and therefore more less attraction)
            # new_value = (((old_value - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min
            if attraction_cntr == 9:
                # print("HERE!!")
                prev_cent_attr = center_attr
                center_attr = (AF7_alpha - AF8_alpha)/(AF8_alpha + AF7_alpha)
                if center_attr < min_value_cent:
                    min_value_cent = center_attr
                if center_attr > max_value_cent:
                    max_value_cent = center_attr
                if first_centr:
                    center_attr_final = (center_attr - min_value_cent) / (1 - min_value_cent) * (0.7 - (-0.5)) + (-0.5)
                    first_centr = False
                else:
                    center_attr_final = (center_attr - min_value_cent) / (max_value_cent - min_value_cent) * (0.01 - (-0.01)) + (-0.01)
                center_attr = (((center_attr - (-1))) * (0.7 - (-0.5)) / (1 - (-1)) + (-.5))
                bt_ratio = (AF8_theta/AF8_beta)
                if bt_ratio < min_value_bt:
                    min_value_bt = bt_ratio
                if bt_ratio > max_value_bt:
                    max_value_bt = bt_ratio
                prev_bt_final =  bt_final
                # print(max_value_bt, min_value_bt)
                if first_bt:
                    bt_final = (bt_ratio - min_value_bt) / (1 - min_value_bt) * (0.5 - (-0.4)) + (-0.4)
                    first_bt = False
                bt_final = (bt_ratio - min_value_bt) / (max_value_bt - min_value_bt) * (0.3 - (-0.13)) + (-0.13)
                #Check if bt_ratio is pos or negative to change range of mouse coordinates
                # print("coords: ", x_coord, y_coord)
                if bt_final < 0:
                    x_coord = (((x_coord - (-1))) * (0.02 - (-0.02)) / (1 - (-1))) + (-0.02)
                    y_coord = (((y_coord - (-1))) * (0.02 - (-0.02)) / (1 - (-1))) + (-0.02)
                if bt_final >= 0:
                    # print("MADE IT!")
                    # print("coords: ", x_coord, y_coord)
                    if x_coord >= 0 and x_coord <= 0.05 and y_coord >= 0 and y_coord <= 0.05:
                        #Quadrant 1 calculation
                        x_coord = x_coord + 0.05
                        y_coord = y_coord + 0.05
                        print("quadrant 1: ", x_coord, y_coord)
                    if x_coord >= -0.05 and x_coord <= 0 and y_coord >= 0 and y_coord <= 0.05:
                        #Quadrant 2 calculation
                        x_coord = x_coord - 0.05
                        y_coord = y_coord + 0.05
                        print("quadrant 2: ", x_coord, y_coord)
                    if x_coord >= -0.05 and x_coord <= 0 and y_coord >= -0.05 and y_coord <= 0:
                        #Quadrant 3 calculation
                        x_coord = x_coord - 0.05
                        y_coord = y_coord - 0.05
                        print("quadrant 3: ", x_coord, y_coord)
                    if x_coord >= 0 and x_coord <= 0.05 and y_coord >= -0.05 and y_coord <= 0:
                        #Quadrant 4 calculation
                        x_coord = x_coord + 0.05
                        y_coord = y_coord - 0.05
                        print("quadrant 4: ", x_coord, y_coord)

                if abs((bt_final/center_attr_final)) > 8:
                    bt_final = prev_bt_final
                    center_attr_final = prev_cent_attr
                attraction_cntr = 0
                # Map range (0, 2) to (-.5, 0.8)
                # tb_ratio = (((tb_ratio - (0)) * (0.8 - (-0.5))) / (2 - 0)) + (-.5)
                

            # Calculate mouse attraction coefficient
            
            # bt_final = 0.5
            # center_attr_final= 0.05
            print("bt_ratio: ", bt_final)
            print("center_attr: ", center_attr_final)
            print("atraction ratio: ", bt_final/center_attr_final)
            print("x coord: ", x_coord)
            print("y coord: ", y_coord)
            # print the ratio between attracion params and see what the ratios are when the partciles explode off the map or shrink too small and keep the ratio within a range that will keep the particles in the frame

            # center_attr = (center_attr + 1) * 0.195 + 0.205

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

            data = [x_coord, y_coord, center_attr_final, bt_final]
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
server_address = ('localhost', 14739)
server = BlockingOSCUDPServer(server_address, dispatcher)
print(f"Listening for OSC messages on {server_address[0]}:{server_address[1]}...")
server.serve_forever()
