#!/usr/bin/env python3
from matplotlib import pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import Tuple
from scipy.signal import savgol_filter

KM_H = True

@dataclass
class DataPoint:
    time: float
    xs: list[float]


def read_data(filename) -> list[DataPoint]:
    """
    Read data points from a CSV file.
    :param filename: The file to read from.
    :return: A list of data points.
    """
    # First line: time;x;y
    data = np.genfromtxt(filename, delimiter=',', skip_header=1)
    data_points = []
    for timestamp, x, _ in data:
        if len(data_points) > 0 and timestamp == data_points[-1].time:
            data_points[-1].xs.append(x)
        else:
            data_points.append(DataPoint(timestamp, [x]))
    return data_points

# TEMP
def filter_points(
        data_points: list[DataPoint]
    ) -> list[Tuple[float, float]]:
    """
    Filter the data points so that it makes a single continuous line.

    :param data_points: The data points to filter.
    :return: The filtered data points.
    """
    sorted_data_points = sorted(data_points, key=lambda x: x.time)
    # Flatten the list of data points into a list of (time, x) tuples.
    sorted_data_points = [
        (data_point.time, data_point.xs[0])
        for data_point in sorted_data_points
    ]
    return sorted_data_points

def map_points_to_real_position(
    data_points: list[Tuple[float, float]],
    point_filter: callable
) -> list[Tuple[float, float]]:
    """
    Map the data points to real-world positions in meters.

    :param data_points: The data points to map.
    :param point_filter: A function that takes an x value (pixels) and returns
    a new x value (meters).
    :return: The mapped data points.
    """
    data_points = [
        (time, point_filter(x))
        for time, x in data_points
    ]
    return data_points

# TEMP
def point_filter(x: float) -> float:
    """
    Filter a single x value.

    :param x: The x value to filter.
    :return: The filtered x value.
    """
    # The runway is 20 meters long and covers the entire width of the image,
    # which is 1280 pixels.
    return x * (20 / 1280)

def get_speeds(
    data_points: list[Tuple[float, float]]
) -> list[Tuple[float, float]]:
    """
    Calculate the speed of the runner between each data point.

    :param data_points: The real world data points (which are in meters).
    :return: The speeds.
    """
    speeds = []
    for i in range(len(data_points) - 1):
        # Calculate the speed between two points.
        time1, x1 = data_points[i]
        time2, x2 = data_points[i + 1]
        speed = (x2 - x1) / (time2 - time1)
        mean_time = (time1 + time2) / 2
        if KM_H:
            speeds.append((mean_time, abs(speed) * 3.6))
        else:
            speeds.append((mean_time, abs(speed)))
    return speeds

def plot_data(
    data_points: list[Tuple[float, float]],
    speeds: list[Tuple[float, float]],
    raw_data_points: list[Tuple[float, float]]
):
    """
    Plot the data points and speeds.

    :param data_points: The data points to plot.
    :param speeds: The speeds to plot.
    """

    ax = plt.axes()

    # Plot the data points.
    plt.plot(*zip(*data_points), color='green')

    # Plot the raw data points.
    # plt.plot(*zip(*raw_data_points), label='Raw data points', color='blue')

    twin = ax.twinx()

    # Plot the speeds.
    twin.plot(*zip(*speeds), label='Vitesse', color='blue')

    # Add labels.
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Distance du côté gauche (m)')
    if KM_H:
        twin.set_ylabel('Vitesse (km/h)')
    else:
        twin.set_ylabel('Vitesse (m/s)')
    twin.set_ylim(0, None)

    # Add a legend.
    plt.legend()
    twin.legend()

    # Show the plot.
    plt.show()

if __name__ == '__main__':
    data_points = read_data('positions.csv')
    data_points = filter_points(data_points)
    data_points = map_points_to_real_position(data_points, point_filter)
    data_points_smoothed = list(savgol_filter(data_points, min(51, len(data_points)), 3, axis=0))
    speeds = get_speeds(data_points_smoothed)
    # smoothed_speeds = list(savgol_filter(speeds, 51, 3, axis=0))
    plot_data(data_points_smoothed, speeds, data_points)
