#!/usr/bin/env python3

"""
This file is used to plot RGB data collected from the color sensor.
It should be run on your computer, not on the robot.

Before running this script for the first time, you must install the dependencies
as explained in the README.md file.
"""

from ast import literal_eval
from math import sqrt, e, pi
from statistics import mean, stdev

from matplotlib import pyplot as plt
import numpy as np


COLOR_SENSOR_DATA_FILE = "color_sensor.csv"


def gaussian(x, values):
    "Return a gaussian function from the given values."
    sigma = stdev(values)
    return (1 / (sigma * sqrt(2 * pi))) * e ** (-((x - mean(values)) ** 2) / (2 * sigma ** 2))


red, green, blue = [], [], []
with open(COLOR_SENSOR_DATA_FILE, "r") as f:
    for line in f.readlines():
        r, g, b = literal_eval(line)  # convert string to 3 floats
        # normalize the values to be between 0 and 1

        ### UNIT-VECTOR METHOD ###
        # denominator = sqrt(r ** 2 + g ** 2 + b ** 2)

        ### RATIO METHOD ###
        denominator = r + g + b
        
        red.append(r / denominator)
        green.append(g / denominator)
        blue.append(b / denominator)


x_values = np.linspace(0, 1, 255)  # 255 evenly spaced values between 0 and 1
plt.plot(x_values, gaussian(x_values, red), color="r")
plt.plot(x_values, gaussian(x_values, green), color="g")
plt.plot(x_values, gaussian(x_values, blue), color="b")
plt.xlabel("Normalized intensity value")
plt.ylabel("Normalized intensity PDF by color")
plt.show()
