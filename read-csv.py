import numpy as np
from matplotlib import pyplot as plt

with open('positions.csv', 'r') as file:
    # for line in file:
    #     # 3 comma-separated values: int, float, float
    #     id, x, y = line.split(',')
    data = np.loadtxt(file, delimiter=';', skiprows=0)

# Make two plots for x and y
plt.plot(data[:, 0], data[:, 1], label='x', marker='.', linestyle=' ')
# plt.plot(data[:, 0], data[:, 2], label='y', marker='.', linestyle=' ')
plt.legend()
plt.show()
