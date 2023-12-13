from matplotlib import pyplot as plt
import numpy as np

# First line: time;x;y

# Read data
data = np.genfromtxt('positions.csv', delimiter=',', skip_header=1)

# Plot data
plt.plot(data[:, 0], data[:, 1], marker='o', linestyle=' ')
plt.show()
