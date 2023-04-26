from GOL import *
import csv
import random

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


replicator_rule = [[None for i in range(65)] for j in range(65)]
count = 0
frames = 25
colors = []
while True:
    while frames <= 25:
        i = 0
        nums = AF_alpha_to_theta[count * 250: 250*(count + 1)]
        nums2 = AF_alpha_to_beta[count * 250: 250 *(count + 1)]
        nums3 = TP_alpha_to_beta[count * 250: 250 * (count + 1)]
        nums4 = sum(TP_alpha_to_theta[count * 250: 250 * (count + 1)]) / 250
        nums5 = sum(AF_gamma_to_alpha) / len(AF_gamma_to_alpha) / 2.5
        interval4 = 0.45
        while 10 * i < len(nums):
            avg1 = sum(nums[10 * i: 10 * (i + 1)]) / 10
            avg2 = sum(nums[10 * i: 10 * (i + 1)]) / 10 / 4225
            rgb = value_to_rgb(avg1, nums4)
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            avg = (sum(nums2[10 * i: 10 * (i + 1)]) + sum(nums3[10 * i: 10 * (i + 1)]))/ 10 / 2
            x = int(avg // 65)
            y = int(avg % 65)
            replicator_rule[x][y] = Color(r, g, b)
            i = i + 1
        chaotic_rules = [[[1,4,6], [8], [8], [2,5]],
                        [[2,5], [1,2], [1,5,6], [7]],
                        [[1,3,5], [1,3,5,7], [1,3,5,7]],
                        [[1,4,7], [2,4,5,6,7]],
                        [[1,3], [7], [1,2,3,6], [3,8]],
                        [[1,2,4,6], [2,4,5]],
                        [[1,7], [3,6], [1,2,5], [6,8]],
                        [[1], [1,4,5]],
                        [[1, 5, 8], [5,8], [1,2,3,4]],
                        [[1,8], [1,7], [1,6], [1,5], [1,4], [1,3], [1,2], [1]]]
        middle_rules = [[[1,4,5], [2,4,5], [1,3,5,7]],
                        [[1,2,3,4], [1,2,3,4,5]],
                        [[1,2,3,8], [2], [4,5]],
                        [[1,3,5], [2,4]],
                        [[1,3,4,5,6,7], [2,8]],
                        [[1,4,5,7], [2]],
                        [[1,2], [3,4], [5,6], [7,8], [1,5], [2,4], [3]],
                        [[2,6], [1,2,3,4]],
                        [[1,6,7,8], [3,4,5,6,7,8]],
                        [[1,2,5], [2,6,8]]]
        stable_rules = [[[1,2,3,4], [1,2,3,4,5]],
                        [[1,2,4,5], [2,4,5,6,8]],
                        [[1,2,3,4,5,6,7,8], [3,6], [3,4,5,6]],
                        [[1,2,3,4,5,6,7,8], [1,8], [4,5,6,7], [2,3]],
                        [[2,3,4], [1]],
                        [[2,3,4], [1,4]],
                        [[1,2,3,4,5,6], [2,3,4,5], [3,4]],
                        [[1,2,3,4,5,6,7,8], [1,2,3,4,5,6,7,8]],
                        [[2,4,5,8], [1,4,5,6,7,8]],
                        [[1,2,3,4], [5,6,7,8], [1,4], [2,3]]]


        def get_threshold(value):
            if value < 0.333:
                return stable_rules[random.randrange(0,9)]
            elif value < 0.666:
                return middle_rules[random.randrange(0,9)]
            else:
                return chaotic_rules[random.randrange(0,9)]
        colorful_animation_limited(replicator_rule, frames, hard_boundary=False, rule= get_threshold(nums5), interval=(750/nums5) , cell_size=.1)





day_and_night_rule = []
size = 100 #should be even
density = .6
rand_grid = random_grid(size//2, size, density) + random_grid(size//2, size, 1-density)
# making this grid reverse symmetric across the horizontal and vertical to show off the symmetric properties of the day and night rule
for j in range(size):
	row=[]
	for i in range(size):
		if i<size/2:
			if j<size/2:
				cell = rand_grid[j][i]
			else:
				cell = 1-rand_grid[size-j-1][i]
		else:
			if j<size/2:
				cell = 1-rand_grid[j][i]
			else:
				cell = rand_grid[size-j-1][i]
		row.append(cell)
	day_and_night_rule.append(row)
day_and_night_rule = random_colors(day_and_night_rule)
#colorful_animation(day_and_night_rule, hard_boundary=False, rule=[[3,6,7,8],[3,4,6,7,8]], interval=150, cell_size=.05)
#save_as_mp4(day_and_night_rule, 200, "day_and_night_rule.mp4", hard_boundary=False, rule=[[3,6,7,8],[3,4,6,7,8]], interval=150, cell_size=.05)
