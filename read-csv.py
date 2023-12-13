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

# Triggers over the whole length of the track
triggers = [i for i in range(500, 0, -25)]

# The conversion between the trigger index and the real world position in meters.
# We know that the total length is 40 meters, so we can use that to calculate the position of each trigger
trigger_map = [i * 40 / len(triggers) for i in range(len(triggers))]

print(trigger_map, triggers)

passes = []

def pos_to_trigger(pos):
    for i, trigger in enumerate(triggers):
        if pos > trigger:
            return i
    return -1

prev_trigger = -1

for data_point in data[1:]:
    trigger = pos_to_trigger(data_point[1])
    if trigger != prev_trigger:
        passes.append([data_point[0], trigger])
        prev_trigger = trigger

passes = np.array(passes)

print(passes)

# Map the passes to the real world position
passes[:, 1] = [trigger_map[int(i)] for i in passes[:, 1]]


speeds = [
    (passes[i+1, 1] - passes[i, 0]) / (passes[i+1, 0] - passes[i, 0])
    for i in range(len(passes) - 1)
]


# Plot the data
fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(passes[:, 1], passes[:, 0], label='time to arrive', marker='.', linestyle='-', color='blue')

# Use the same x axis for both plots
ax2 = ax.twinx()

speed_x = passes[:-1, 1] + (passes[1:, 1] - passes[:-1, 1]) / 2

ax2.plot(speed_x, speeds, label='speed', marker='.', linestyle='-', color='red')

# Add legend
ax.legend(loc='upper left')
ax2.legend(loc='upper right')

# Add labels on the axes
ax.set_xlabel('Position (m)')
ax.set_ylabel('Time (s)')
ax2.set_ylabel('Speed (m/s)')

# Make all axes start at 0
ax.set_xlim(0, 40)
ax.set_ylim(0, None)
ax2.set_ylim(0, None)

plt.show()
