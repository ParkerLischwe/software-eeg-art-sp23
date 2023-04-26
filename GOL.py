import math
import random
from random import uniform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anm
import matplotlib.colors as clrs
import csv
import os
import imageio
from PIL import Image
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
import numpy as np
import csv
import datetime
import queue
import threading
import select
import time

def it_got_to_max(address, *args):
    print("Max data recieved: ", args)
if os.path.exists(eeg_data3.csv):
    with open(eeg_data3.csv, 'w') as f:
def write_data_to_csv(data):
    with open('eeg_data3.csv', mode='a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(data)

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
num_fft_calc = 0
sample_factor = 1
sample_counter = 0

# counter variable controls the sliding window granularity (5 waits for 5 points to make next fft calculation)
counter = 2

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
    global num_samples_processed, sample_factor, counter, sample_counter, num_fft_calc
    global ch1_buff, ch2_buff, ch3_buff, ch4_buff
    global oldest_idx1, newest_idx1, oldest_idx2, newest_idx2
    global oldest_idx3, newest_idx3, oldest_idx4, newest_idx4
    sample_id = args[0]
    unix_ts = args[1] + args[2]
    lsl_ts = args[3] + args[4]
    data = args[5:]

    # This chunk controls how much data we sample from the incoming stream.
    # When equal to 1 we sample every data point in the stream
    sample_counter += 5
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

    if num_samples_processed >= 512:
        counter += 1
        if counter == 3:
            counter = 0
            # print(ch1_buff.size)
            channel1_fft = np.fft.fft(ch1_buff.buffer)[:256]
            num_fft_calc += 1
            print(num_fft_calc)
            ch1_gamma = np.sum(np.abs(channel1_fft[32:100]))
            ch1_beta = np.sum(np.abs(channel1_fft[13:32]))
            ch1_alpha = np.sum(np.abs(channel1_fft[4:8]))
            ch1_theta = np.sum(np.abs(channel1_fft[0:4]))

            # Process ch2 data
            channel2_fft = np.fft.fft(ch2_buff.buffer)[:256]
            ch2_gamma = np.sum(np.abs(channel2_fft[32:100]))
            ch2_beta = np.sum(np.abs(channel2_fft[13:32]))
            ch2_alpha = np.sum(np.abs(channel2_fft[4:8]))
            ch2_theta = np.sum(np.abs(channel2_fft[0:4]))

            # Process ch3 data
            channel3_fft = np.fft.fft(ch3_buff.buffer)[:256]
            ch3_gamma = np.sum(np.abs(channel3_fft[32:100]))
            ch3_beta = np.sum(np.abs(channel3_fft[13:32]))
            ch3_alpha = np.sum(np.abs(channel3_fft[4:8]))
            ch3_theta = np.sum(np.abs(channel3_fft[0:4]))

            # Process ch4 data
            channel4_fft = np.fft.fft(ch4_buff.buffer)[:256]
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
            data2 = [ch1_gamma, ch1_beta, ch1_alpha, ch1_theta, ch2_gamma, ch2_beta, ch2_alpha, ch2_theta, ch3_gamma, ch3_beta, ch3_alpha, ch3_theta, ch4_gamma, ch4_beta, ch4_alpha, ch4_theta]
            print("Data is here: ", data2)

    num_samples_processed += 1
    # Write the data to the CSV file
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    data_row = [timestamp] + list(data2)
    write_data_to_csv(data_row)


# Create a dispatcher object and register the callback function with it
dispatcher = Dispatcher()
dispatcher.map("/PetalStream/eeg", process_eeg_signal)

# Create a server object and start listening for OSC messages
server_address = ('localhost', 1337)
server = BlockingOSCUDPServer(server_address, dispatcher)
print(f"Listening for OSC messages on {server_address[0]}:{server_address[1]}...")

timeout = 20  # Timeout in seconds
start_time = time.monotonic()  # Start time
while True:
    # Compute remaining time
    elapsed_time = time.monotonic() - start_time
    remaining_time = timeout - elapsed_time
    if remaining_time < 0:
        break  # Timeout exceeded, exit loop

    # Wait for incoming requests with timeout
    readable, _, _ = select.select([server.socket], [], [], remaining_time)
    if readable:
        server.handle_request()

server.server_close()

input_file = "eeg_data3.csv"
output_file = "alpha_beta_theta_gamma.csv"

if os.path.exists(output_file):
    with open(output_file, 'w') as f:
        pass

with open(input_file, 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    header = next(csv_reader)  # Skip header row
    ratios = []
    for row in csv_reader:
        timestamp = row[0]
        af7_gamma, af7_beta, af7_alpha, af7_theta, af8_gamma, af8_beta, af8_alpha, af8_theta, tp9_gamma, tp9_beta, tp9_alpha, tp9_theta, tp10_gamma, tp10_beta, tp10_alpha, tp10_theta = map(float, row[1:])
        af_alpha_beta = (af7_alpha + af8_alpha) / (af7_beta + af8_beta)
        af_alpha_theta = (af7_alpha + af8_alpha) / (af7_theta + af8_theta)
        af_gamma_theta = (af7_gamma + af8_gamma) / (af7_theta + af8_theta)
        af_gamma_beta = (af7_gamma + af8_gamma) / (af7_beta + af8_beta)
        tp_alpha_beta = (tp9_alpha + tp10_alpha) / (tp9_beta + tp10_beta)
        tp_alpha_theta = (tp9_alpha + tp10_alpha) / (tp9_theta + tp10_theta)
        tp_gamma_theta = (tp9_gamma + tp10_gamma) / (tp9_theta + tp10_theta)
        tp_gamma_beta = (tp9_gamma + tp10_gamma) / (tp9_beta + tp10_beta)
        ratios.append([af_alpha_beta, af_alpha_theta, af_gamma_theta, af_gamma_beta, tp_alpha_beta, tp_alpha_theta, tp_gamma_theta, tp_gamma_beta])

# Write output to csv
with open(output_file, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["AF Alpha/Beta", "AF Alpha/Theta", "AF Gamma/Theta", "AF Gamma/Beta", "TP Alpha/Beta", "TP Alpha/Theta", "TP Gamma/Theta", "TP Gamma/Beta"])
    writer.writerows(ratios)

AF_alpha_to_beta = []
AF_alpha_to_theta = []
AF_gamma_to_alpha = []
AF_gamma_to_beta = []
TP_alpha_to_beta = []
TP_alpha_to_theta = []
TP_gamma_to_alpha = []
TP_gamma_to_beta = []

with open('alpha_beta_theta_gamma.csv', 'r') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the first row
    next(csv_reader)

    # Iterate through each row in the CSV file
    for row in csv_reader:
        # Extract the values and convert them to floats
        AF_alpha_beta_ratio = float(row[0])
        AF_alpha_theta_ratio = float(row[1])
        AF_gamma_alpha_ratio = float(row[2])
        AF_gamma_beta_ratio = float(row[3])
        TP_alpha_beta_ratio = float(row[4])
        TP_alpha_theta_ratio = float(row[5])
        TP_gamma_alpha_ratio = float(row[6])
        TP_gamma_beta_ratio = float(row[7])

        # Perform the division and append to the respective lists
        AF_alpha_to_beta.append(round(AF_alpha_beta_ratio / 0.00047337278))
        AF_alpha_to_theta.append(AF_alpha_theta_ratio)
        AF_gamma_to_alpha.append(AF_gamma_alpha_ratio)
        AF_gamma_to_beta.append(AF_gamma_beta_ratio)
        TP_alpha_to_beta.append(round(TP_alpha_beta_ratio / 0.00047337278))
        TP_alpha_to_theta.append(TP_alpha_theta_ratio)
        TP_gamma_to_alpha.append(TP_gamma_alpha_ratio)
        TP_gamma_to_beta.append(TP_gamma_beta_ratio)

#rand_grid = random_colors(random_grid(25, 25))
#colorful_animation(rand_grid)
#save_as_gif(rand_grid, 100, "random_example.gif") # this can take a minute and will only start after the animation window from the previous line is closed


def value_to_rgb(val, brightness):
    value = val * 2
    if value < 0.01:
        r = 0
        g = 0
        b = 0
    elif value < 0.15:
        r = 176
        g = 48
        b = 96
    elif value < 0.3:
        r = 236
        g = 88
        b = 135
    elif value < 0.45:
        r = 128
        g = 0
        b = 128
    elif value < 0.6:
        r = 30
        g = 30
        b = 160
    elif value < 0.75:
        r = 100
        g = 149
        b = 237
    elif value < 0.9:
        r = 0
        g = 255
        b = 255
    elif value < 1.05:
        r = 0
        g = 255
        b = 127
    elif value < 1.2:
        r = 50
        g = 205
        b = 50
    elif value < 1.35:
        r = 255
        g = 255
        b = 0
    elif value < 1.5:
        r = 255
        g = 165
        b = 0
    elif value < 1.65:
        r = 255
        g = 69
        b = 0
    elif value < 1.8:
        r = 255
        g = 0
        b = 0
    elif value < 2.00:
        r = 255
        g = 0
        b = 255
    else:
        r = 255
        g = 0
        b = 255
    return r * brightness * 1.3, g * brightness * 1.3, b * brightness * 1.3

def colored_grid_changer(count):
    nums = AF_alpha_to_theta[count * 250: 250 * (count + 1)]
    nums2 = AF_alpha_to_beta[count * 250: 250 * (count + 1)]
    nums3 = TP_alpha_to_beta[count * 250: 250 * (count + 1)]
    nums4 = sum(TP_alpha_to_theta[count * 250: 250 * (count + 1)]) / 250
    i = 0
    replicator_rule = [[None for i in range(65)] for j in range(65)]
    while 10 * i < len(nums):
        avg1 = sum(nums[10 * i: 10 * (i + 1)]) / 10
        avg2 = sum(nums[10 * i: 10 * (i + 1)]) / 10
        rgb = value_to_rgb(avg1, nums4)
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        avg = (sum(nums2[10 * i: 10 * (i + 1)]) + sum(nums3[10 * i: 10 * (i + 1)])) / 10 / 2
        x = int(avg // 65)
        y = int(avg % 65)
        if x >= 65:
            x = 64
        if y >= 65:
            y = 65
        replicator_rule[x][y] = Color(r, g, b)
        i = i + 1
    return replicator_rule


class Color:
    """This is a class to represent colors as RGB triples."""

    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b})"

    def __str__(self):
        return f"({self.r}, {self.g}, {self.b})"

    def __add__(self, other):
        if isinstance(other, Color):
            r = min(self.r + other.r, 255)
            g = min(self.g + other.g, 255)
            b = min(self.b + other.b, 255)
            return Color(r, g, b)
        raise TypeError("Unsupported operand for +: 'Color' and " + str(type(other)))

    def __sub__(self, other):
        if isinstance(other, Color):
            r = max(self.r - other.r, 0)
            g = max(self.g - other.g, 0)
            b = max(self.b - other.b, 0)
            return Color(r, g, b)
        raise TypeError("Unsupported operand for -: 'Color' and " + str(type(other)))

    def __eq__(self, other):
        if isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b
        return False

    def __ne__(self, other):
        return not self.__eq__(other)



def average_hue(list_of_hues):
    """
    Gets the average hue from a list of hues.

    Parameters:
    list_of_hues (list of Hue objects)

    Returns:
    Hue
    """

    red = 0.0
    green = 0.0
    blue = 0.0
    count = 0
    # Take all the hues as points on a unit circle and average their coordinates to find the average
    for hue in list_of_hues:
        red += hue.r
        blue += hue.b
        green += hue.g
        count = count + 1
    red = red / count
    green = green / count
    blue = blue / count
    return Color(red, blue, green)


def random_grid(height, width, density=.3, padding=0):
    """
    Gives a random 2D grid of 1s and 0s.

    Parameters:
    height (int): How many rows the grid will have
    width (int): How many columns the grid will have
    density (float): The probability any given cell will be a 1
    padding (int): If a padding value is specified, cells within the padding distance of an edge will always be 0

    Returns:
    2D list
    """

    if not padding:
        return [[1 if random() < density else 0 for x in range(width)] for y in range(height)]
    else:
        return [[(1 if random() < density else 0) if (not (x < padding or x >= width - padding)) and (
            not (y < padding or y >= height - padding)) else 0 for x in range(width)] for y in range(height)]


def random_colors(grid):
    """
    Gives random colors to a grid of cells.

    Parameters:
    grid (2D list): Any cell that evaluates to True will become a random color

    Returns:
    2D list of Hue objects
    """
    red = random.randrange(256)
    blue = random.randrange(256)
    green = random.randrange(256)
    return [[Color(red, blue, green) if cell else None for cell in row] for row in grid]


def colorful_life_step(colored_grid, color_variation=0.05, hard_boundary=True, rule=[[3], [2, 3]]):
    """
    Runs a step for The Colorful Game of Life.

    The Colorful Game of Life has the same rules as Conway's Game of Life, except that all living cells also have a color assigned to them. When a new cell is born, it will take on the average color of its parents. Color variation can be added so that newly born cells can deviate slightly in color. Living cells will keep their color fixed until they die.

    Parameters:
    colored_grid (2D list of Color objects): The grid that should be stepped through
    color_variation (float): A newly born cell will deviate from its color randomly up or down, with this amount being the maximum possible deviation.
    hard_boundary (bool): Setting this to False will identify opposite edges so that cells touching the boundary will communicate with cells on the other side of the grid.
    rule (2D list of integers): The first set of elements is how many neighbors leads to a birth, and the second is how many neighbors lead to a cell surviving.

    Returns:
    2D list of Color objects
    """

    height = len(colored_grid)
    width = len(colored_grid[0])
    next_grid = []
    if not hard_boundary:
        if width >= 3 and height >= 3:
            for j in range(height):
                row = []
                for i in range(width):
                    live_neighbors = [colored_grid[(j + a) % height][(i + b) % width] for a in (-1, 0, 1) for b in
                                      (-1, 0, 1) if
                                      ((a != 0 or b != 0) and colored_grid[(j + a) % height][(i + b) % width])]
                    neighbor_count = len(live_neighbors)
                    if colored_grid[j][i]:
                        if neighbor_count in rule[1]:
                            row.append(colored_grid[j][i])
                        else:
                            row.append(None)
                    else:
                        if neighbor_count in rule[0]:
                            color = average_hue(live_neighbors)
                            color.r += uniform(-color_variation, color_variation)
                            color.g += uniform(-color_variation, color_variation)
                            color.b += uniform(-color_variation, color_variation)
                            row.append(color)
                        else:
                            row.append(None)
                next_grid.append(row)
            return next_grid
        else:
            # Need to tweak things so cells aren't double-counted
            for j in range(height):
                row = []
                for i in range(width):
                    if height >= 3:
                        # width is short
                        live_neighbors = [colored_grid[(j + a) % height][(i + b) % width] for a in (-1, 0, 1) for b in
                                          range(width) if (
                                                  (a != 0 or b != 0) and colored_grid[(j + a) % height][(i + b) % width])]
                    elif width >= 3:
                        # height is short
                        live_neighbors = [colored_grid[(j + a) % height][(i + b) % width] for a in range(height) for b
                                          in (-1, 0, 1) if (
                                                  (a != 0 or b != 0) and colored_grid[(j + a) % height][(i + b) % width])]
                    else:
                        # width and height are short
                        live_neighbors = [colored_grid[(j + a) % height][(i + b) % width] for a in range(height) for b
                                          in range(width) if (
                                                  (a != 0 or b != 0) and colored_grid[(j + a) % height][
                                              (i + b) % width])]

                        neighbor_count = len(live_neighbors)
                        if colored_grid[j][i]:
                            if neighbor_count in rule[1]:
                                row.append(colored_grid[j][i])
                            else:
                                row.append(None)
                        else:
                            if neighbor_count in rule[0]:
                                color = average_hue(live_neighbors)
                                color.r += uniform(-color_variation, color_variation)
                                color.g += uniform(-color_variation, color_variation)
                                color.b += uniform(-color_variation, color_variation)
                                row.append(color)
                            else:
                                row.append(None)
                next_grid.append(row)
                return next_grid
            else:
                # Implementing the hard boundary logic
                for j in range(height):
                    row = []
                    for i in range(width):
                        live_neighbors = [
                            colored_grid[j + a][i + b] if 0 <= j + a < height and 0 <= i + b < width else None for
                            a in (-1, 0, 1) for b in (-1, 0, 1) if (a != 0 or b != 0)]
                        live_neighbors = [neighbor for neighbor in live_neighbors if neighbor is not None]
                        neighbor_count = len(live_neighbors)
                        if colored_grid[j][i]:
                            if neighbor_count in rule[1]:
                                row.append(colored_grid[j][i])
                            else:
                                row.append(None)
                        else:
                            if neighbor_count in rule[0]:
                                color = average_hue(live_neighbors)
                                color.r += uniform(-color_variation, color_variation)
                                color.g += uniform(-color_variation, color_variation)
                                color.b += uniform(-color_variation, color_variation)
                                row.append(color)
                            else:
                                row.append(None)
                    next_grid.append(row)
                return next_grid


def colorful_animation_limited(colored_grid, number_of_frames, color_variation=0.1, hard_boundary=True,
                               rule=[[3], [2, 3]], interval=1000, cell_size=0.2, show=True, save_filename='animation.gif'):
    """
    This will create an animation of The Colorful Game of Life using Matplotlib. The animation will run for a limited number of steps and then restart.

    Parameters:
    colored_grid (2D list of Hue objects): The starting grid.
    number_of_frames (int): How many steps until the animation restarts.
    color_variation (float): A newly born cell will deviate from its color randomly up or down, with this amount being the maximum possible deviation.
    hard_boundary (bool): Setting this to False will identify opposite edges so that cells touching the boundary will communicate with cells on the other side of the grid.
    rule (2D list of integers): The first set of elements is how many neighbors leads to a birth, and the second is how many neighbors lead to a cell surviving.
    interval (int): The number of milliseconds each step should take in the animation.
    cell_size (float): The number of inches per side of each cell.
    show (bool): If this is True, the animation will open.

    Returns:
    An Animation object
    """

    # Define width and height variables
    width = len(colored_grid[0])
    height = len(colored_grid)

    def grid_to_array(grid):
        height = len(grid[0])
        width = len(grid[0])
        X = np.empty((height, width, 3), dtype=np.float32)
        for i in range(height):
            for j in range(width):
                if grid[i][j] is None:
                    X[i][j] = [0.0, 0.0, 0.0]  # Set to black for None values
                else:
                    # Extract RGB values from Color object
                    X[i][j] = [grid[i][j].r / 255.0, grid[i][j].g / 255.0, grid[i][j].b / 255.0]
        return X

    def animate(frame):
        plt.cla()
        ax.imshow(frame, cmap='viridis', norm=clrs.Normalize(vmin=0, vmax=1),
                  interpolation='nearest')

    fig = plt.figure(figsize=(width * cell_size, height * cell_size))
    ax = fig.add_axes([0, 0, 1, 1], xticks=[], yticks=[], frameon=False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    fig.patch.set_facecolor('black')

    def save_as_gif(frames, filename, duration=0.1):
        """
        Saves the given frames as a GIF file.

        Parameters:
        frames (list of numpy arrays): The frames to save.
        filename (str): The filename of the GIF file to create.
        duration (float): The duration (in seconds) of each frame in the GIF.

        Returns:
        None
        """
        with imageio.get_writer(filename, mode='I', duration=duration) as writer:
            for frame in frames:
                writer.append_data((frame * 255).astype('uint8'))

    counter = 1
    interval2 = sum(AF_gamma_to_alpha) / len(AF_gamma_to_alpha)
    interval3 = 750 / interval2

    frames = []  # Initialize an empty list to store frames
    for i in range(1000):
        frames.append(grid_to_array(colored_grid))
        colored_grid = colorful_life_step(colored_grid, color_variation, hard_boundary, rule)
        if (i != 0 and i % 24 == 0):
            colored_grid = colored_grid_changer(counter)
            counter = counter + 1
            nums5 = sum(AF_gamma_to_alpha[counter * 250: 250 * (counter + 1)]) / 250
        if (len(frames) == 200):
            save_as_gif(frames, "test6.gif", duration=0.1)

    anim = anm.FuncAnimation(fig, animate, frames=frames, interval= interval3)
    if show:
        plt.show()
    return anim
