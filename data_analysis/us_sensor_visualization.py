#!/usr/bin/env python3

"""
This file is used to plot continuous data collected from the ultrasonic sensor.
It should be run on your computer, not on the robot.

Before running this script for the first time, you must install the dependencies
as explained in the README.md file.
"""

from matplotlib import pyplot as plt

US_SENSOR_DATA_FILE = "us_sensor.csv"
DELAY_SEC = 0.01

with open(US_SENSOR_DATA_FILE, "r") as f:
    distances = [float(d) for d in f.readlines()]

times = [DELAY_SEC * i for i in range(len(distances))]

# You can customize the plot below, eg, by changing the color
plt.plot(times, distances)
plt.xlabel("Time (s)")
plt.ylabel("Distance (cm)")
plt.yticks([d for d in range(round(max(distances)) + 10) if d % 10 == 0])
plt.show()
