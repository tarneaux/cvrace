import numpy as np
from matplotlib import pyplot as plt

with open('positions.csv', 'r') as file:
    # for line in file:
    #     # 3 comma-separated values: int, float, float
    #     id, x, y = line.split(',')
    data = np.loadtxt(file, delimiter=';', skiprows=0)

data = data[:, 0:2]

# Offset timing to start at 0
data[:, 0] -= data[0, 0]

# Make the time be in seconds
data[:, 0] /= 1000

# Triggers every 5 meters
triggers = [i for i in range(500, 50, -50)]

passes = []

def pos_to_trigger(pos):
    for i, trigger in enumerate(triggers):
        if pos > trigger:
            return i
    return -1

prev_trigger = pos_to_trigger(data[0, 1])

for data_point in data[1:]:
    trigger = pos_to_trigger(data_point[1])
    if trigger != prev_trigger:
        passes.append([data_point[0], trigger])
        prev_trigger = trigger

passes = np.array(passes)

# Make the trigger be in meters
passes[:, 1] = passes[:, 1] * 5

# Make two plots for x and y
plt.plot(passes[:, 0], passes[:, 1], label='pos', marker='.', linestyle='-')

speeds = [
    5 / (passes[i+1, 0] - passes[i, 0])
    for i in range(len(passes) - 1)
]

speed_times = passes[1:, 0] - (passes[1:, 0] - passes[:-1, 0]) / 2

print(passes, speeds)

plt.plot(speed_times, speeds, label='speed', marker='.', linestyle='-')

# Add legend
plt.legend(loc='upper left')

plt.show()
