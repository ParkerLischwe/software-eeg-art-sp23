from GOL import *
import csv
import random

import csv

with open('alpha_to_beta_ratios.csv', 'r') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)
    nums = []
    nums2 = []
    # Skip the first row
    next(csv_reader)
    # Iterate through each row in the CSV file
    for row in csv_reader:
        # Iterate through each value in the row
        for value in row:
            # Convert the value to a float and perform the division
            num = round(float(value) / 0.00146484375)
            nums.append(num)
            nums2.append(float(value))

# Now you can access the calculated values in the nums list
print(nums)
print(nums2)

import numpy as np

# Create a 25x25 grid with None values
rand_grid = [[None for _ in range(25)] for _ in range(25)]

# Add 25 dummy values to the nums array
for i in range(50):
    dummy_value = random.randint(25*i, 25*i + 25)
    nums.append(dummy_value)
nums3 = [
    2300, 2959, 3310, 451, 66, 2798, 1277, 1444, 3535, 4024,
    2704, 2589, 2906, 151, 183, 3452, 3519, 3864, 125, 3465,
    942, 2631, 3197, 128, 3387, 2325, 3890, 280, 2040, 3432,
    976, 1096, 3615, 1987, 3914, 82, 3617, 1429, 3094, 220,
    3780, 2162, 2640, 3297, 1750, 826, 925, 930, 1764, 3633,
    1994, 3549, 3150, 1971, 2461, 2851, 307, 3250, 297, 1825,
    895, 3244, 2610, 2387, 579, 785, 1739, 3088, 3462, 3946,
    1859, 2702, 2363, 4038, 4159, 1305, 3336, 3866, 2859, 4052,
    1428, 2311, 2911, 3068, 3142, 929, 3905, 2301, 1215, 2302,
    2075, 190, 946, 3227, 526, 490, 658, 1868, 595, 1101, 3946,
    815, 2483, 1014, 2446, 2900, 1011, 297, 3341, 315, 2894,
    3441, 2669, 3166, 503, 2701, 1426, 2409, 3896, 2236, 2225,
    1065, 1433, 4160, 1169, 878, 2141, 2990, 1848, 3460, 4122,
    3605, 1319, 1491, 451, 3346, 3510, 3692, 2986, 1299, 4103,
    1459, 1174, 1195, 2391, 1002, 3537, 3396, 3638, 609, 644,
    4007, 2634, 149, 549, 2385, 1983, 2115, 3509, 4174, 2012,
    792, 4025, 1517, 4047, 2926, 2373, 611, 1054, 4130, 3696,
    1500, 1813, 3393, 1395, 3957, 2418, 52, 429, 3543, 2272,
    557, 2432, 3818, 4137, 178, 286, 1419, 2141, 2736, 2171,
    3353, 335]
for num in nums3:
    nums.append(num)

#rand_grid = random_colors(random_grid(25, 25))
#colorful_animation(rand_grid)
#save_as_gif(rand_grid, 100, "random_example.gif") # this can take a minute and will only start after the animation window from the previous line is closed





replicator_rule = [[None for i in range(65)] for j in range(65)]
count = 0;
frames = 25;
while True:
    while frames <= 25:
        nums2 = nums[count * 25: 25*(count + 1)]
        for num in nums2:
        # Calculate x and y coordinates
            x = num // 65
            y = num % 65
            if num < 35:
                replicator_rule[x][y] = Color(128, 0, 0)
            elif num < 140:
                replicator_rule[x][y] = Color(153, 0, 0)
            elif num < 210:
                replicator_rule[x][y] = Color(204, 0, 0)
            elif num < 280:
                replicator_rule[x][y] = Color(255, 0, 0)
            elif num < 350:
                replicator_rule[x][y] = Color(255, 51, 0)
            elif num < 420:
                replicator_rule[x][y] = Color(255, 102, 0)
            elif num < 490:
                replicator_rule[x][y] = Color(255, 153, 51)
            elif num < 560:
                replicator_rule[x][y] = Color(255, 204, 0)
            elif num < 630:
                replicator_rule[x][y] = Color(255, 255, 0)
            elif num < 700:
                replicator_rule[x][y] = Color(255, 255, 102)
            elif num < 770:
                replicator_rule[x][y] = Color(255, 255, 153)
            elif num < 840:
                replicator_rule[x][y] = Color(204, 255, 153)
            elif num < 910:
                replicator_rule[x][y] = Color(204, 255, 102)
            elif num < 980:
                replicator_rule[x][y] = Color(204, 255, 51)
            elif num < 1050:
                replicator_rule[x][y] = Color(153, 204, 0)
            elif num < 1120:
                replicator_rule[x][y] = Color(153, 255, 51)
            elif num < 1190:
                replicator_rule[x][y] = Color(153, 255, 102)
            elif num < 1260:
                replicator_rule[x][y] = Color(102, 255, 51)
            elif num < 1330:
                replicator_rule[x][y] = Color(51, 204, 51)
            elif num < 1400:
                replicator_rule[x][y] = Color(0, 153, 51)
            elif num < 1470:
                replicator_rule[x][y] = Color(0, 204, 102)
            elif num < 1540:
                replicator_rule[x][y] = Color(0, 204, 153)
            elif num < 1610:
                replicator_rule[x][y] = Color(51, 204, 204)
            elif num < 1680:
                replicator_rule[x][y] = Color(0, 153, 204)
            elif num < 1750:
                replicator_rule[x][y] = Color(0, 102, 204)
            else:
                replicator_rule[x][y] = Color(18, 90, 29)
        colorful_animation_limited(replicator_rule, frames, hard_boundary=False, rule=[[1,3,5,7],[1,3,5,7]], interval=150, cell_size=.1)
        frames = frames + 1
    if frames > 25:
        frames = 25
        replicator_rule = [[None for i in range(65)] for j in range(65)]
        count += 1





#save_as_gif(replicator_rule, 190, "replicator_rule.gif", hard_boundary=False, rule=[[1,3,5,7],[1,3,5,7]], interval=150, cell_size=.1) #takes quite a bit of time




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
