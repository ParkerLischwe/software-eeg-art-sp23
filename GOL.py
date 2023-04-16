# The Colorful Game of Life
# Created by Adam Zheleznyak
# https://github.com/adam-zheleznyak/colorful-life

import math
from random import random
from random import uniform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anm
import matplotlib.colors as clrs


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


def colorful_animation(colored_grid, color_variation=0.05, hard_boundary=True, rule=[[3], [2, 3]], interval=300,
                       cell_size=0.2, show=True):
    """
    This will create an animation of The Colorful Game of Life using Matplotlib. The animation will run forever until closed.

    Parameters:
    colored_grid (2D list of Hue objects): The starting grid.
    color_variation (float): A newly born cell will deviate from its color randomly up or down, with this amount being the maximum possible deviation.
    hard_boundary (bool): Setting this to False will identify opposite edges so that cells touching the boundary will communicate with cells on the other side of the grid.
    rule (2D list of integers): The first set of elements is how many neighbors leads to a birth, and the second is how many neighbors lead to a cell surviving.
    interval (int): The number of milliseconds each step should take in the animation.
    cell_size (float): The number of inches per side of each cell.
    show (bool): If this is True, the animation will open.

    Returns:
    An Animation object
    """

    def grid_to_array(grid):
        X = np.asarray(grid)
        X = X.astype(float)
        return X

    height = len(colored_grid)
    width = len(colored_grid[0])

    fig = plt.figure(figsize=(width * cell_size, height * cell_size))
    ax = fig.add_axes([0, 0, 1, 1], xticks=[], yticks=[], frameon=False)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    fig.patch.set_facecolor('black')

    def animate(colored_grid):
        plt.cla()
        ax.imshow(grid_to_array(colored_grid), cmap=plt.cm.hsv, norm=clrs.Normalize(vmin=0, vmax=1),
                  interpolation='nearest')

    def frame_generator(colored_grid, color_variation, hard_boundary, rule):
        yield colored_grid  # for some reason, this generator is being called once before the animation starts, so this is to account for that
        while True:
            yield colored_grid
            colored_grid = colorful_life_step(colored_grid, color_variation, hard_boundary, rule)

    anim = anm.FuncAnimation(fig, animate, frames=frame_generator(colored_grid, color_variation, hard_boundary, rule),
                             interval=interval)

    if show:
        plt.show()

    return anim


def colorful_animation_limited(colored_grid, number_of_frames, color_variation=0.05, hard_boundary=True,
                               rule=[[3], [2, 3]], interval=300, cell_size=0.2, show=True):
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
        height = len(grid)
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

    frames = []

    for i in range(number_of_frames):
        frames.append(grid_to_array(colored_grid))
        colored_grid = colorful_life_step(colored_grid, color_variation, hard_boundary, rule)

    anim = anm.FuncAnimation(fig, animate, frames=frames, interval=interval)

    if show:
        plt.show()


def save_as_html(colored_grid, number_of_frames, filename, color_variation=0.05, hard_boundary=True, rule=[[3], [2, 3]],
                 cell_size=0.2, interval=300):
    """
    Saves the animation as an HTML page.

    Parameters:
    colored_grid (2D list of Hue objects): The starting grid.
    number_of_frames (int): How many steps until the animation restarts.
    filename (str): What the HTML file should be saved as.
    color_variation (float): A newly born cell will deviate from its color randomly up or down, with this amount being the maximum possible deviation.
    hard_boundary (bool): Setting this to False will identify opposite edges so that cells touching the boundary will communicate with cells on the other side of the grid.
    rule (2D list of integers): The first set of elements is how many neighbors leads to a birth, and the second is how many neighbors lead to a cell surviving.
    interval (int): The number of milliseconds each step should take in the animation.
    cell_size (float): The number of inches per side of each cell.
    """

    colorful_animation_limited(colored_grid, number_of_frames, color_variation=color_variation,
                               hard_boundary=hard_boundary, rule=rule, interval=interval, cell_size=cell_size,
                               show=False).save(filename, writer='html', savefig_kwargs={'facecolor': 'black'})
    plt.close()


def save_as_gif(colored_grid, number_of_frames, filename, color_variation=0.05, hard_boundary=True, rule=[[3], [2, 3]],
                cell_size=0.2, interval=300):
    """
    Requires the package 'imagemagick' to be installed.

    Saves the animation as a gif.

    Parameters:
    colored_grid (2D list of Hue objects): The starting grid.
    number_of_frames (int): How many steps until the animation restarts.
    filename (str): What the HTML file should be saved as.
    color_variation (float): A newly born cell will deviate from its color randomly up or down, with this amount being the maximum possible deviation.
    hard_boundary (bool): Setting this to False will identify opposite edges so that cells touching the boundary will communicate with cells on the other side of the grid.
    rule (2D list of integers): The first set of elements is how many neighbors leads to a birth, and the second is how many neighbors lead to a cell surviving.
    interval (int): The number of milliseconds each step should take in the animation.
    cell_size (float): The number of inches per side of each cell.
    """

    colorful_animation_limited(colored_grid, number_of_frames, color_variation=color_variation,
                               hard_boundary=hard_boundary, rule=rule, interval=interval, cell_size=cell_size,
                               show=False).save(filename, writer='imagemagick', savefig_kwargs={'facecolor': 'black'})
    plt.close()


def save_as_mp4(colored_grid, number_of_frames, filename, color_variation=0.05, hard_boundary=True, rule=[[3], [2, 3]],
                cell_size=0.2, interval=300):
    """
    Requires the package 'ffmpeg' to be installed.

    Saves the animation as an mp4 video.

    Parameters:
    colored_grid (2D list of Hue objects): The starting grid.
    number_of_frames (int): How many steps until the animation restarts.
    filename (str): What the HTML file should be saved as.
    color_variation (float): A newly born cell will deviate from its color randomly up or down, with this amount being the maximum possible deviation.
    hard_boundary (bool): Setting this to False will identify opposite edges so that cells touching the boundary will communicate with cells on the other side of the grid.
    rule (2D list of integers): The first set of elements is how many neighbors leads to a birth, and the second is how many neighbors lead to a cell surviving.
    interval (int): The number of milliseconds each step should take in the animation.
    cell_size (float): The number of inches per side of each cell.
    """

    colorful_animation_limited(colored_grid, number_of_frames, color_variation=color_variation,
                               hard_boundary=hard_boundary, rule=rule, interval=interval, cell_size=cell_size,
                               show=False).save(filename, writer='ffmpeg', savefig_kwargs={'facecolor': 'black'})
    plt.close()
