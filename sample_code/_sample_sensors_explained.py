"""sample_sensors_explained

This file serves as a list of example code using the sensors. 
It includes more explanations for the 3 sensors used in this file.

It is meant to be run with the following attached sensors:

Port 1 - TouchSensor
Port 2 - EV3ColorSensor
Port 3 - EV3UltrasonicSensor

It uses 'input' calls to let you get ready to position a sensor and take data.
Usually, sensor data is sampled continuously in a while loop, using a 
time.sleep(seconds) to create an interval between taking sensor sample data.

Author: Ryan Au
January 24th, 2022
"""

### This file should be moved to the project/ folder if you want to run it ###

from utils.brick import wait_ready_sensors, EV3ColorSensor, EV3UltrasonicSensor, TouchSensor

touch = TouchSensor(1) # port S1
color = EV3ColorSensor(2) # port S2
ultra = EV3UltrasonicSensor(3) # port S3

# waits until every previously defined sensor is ready
wait_ready_sensors()

"""
Every sensor has a 'sensor.get_value()' method, 
returning different things for different sensors.

all sensors give 'None' when there is an error
"""
color.get_raw_value() # usually list [r,g,b,intensity], sometimes one number
touch.get_raw_value() # 0 or 1
ultra.get_raw_value() # usually distance, centimeters


#######################
###                 ###
### TOUCH DETECTION ###
###                 ###
#######################

input("Waiting. Press Enter to take Touch Data")
"""Touch sensor has no real setup necessary. One method, returns True/False boolean."""
print(touch.is_pressed())


#######################
###                 ###
### COLOR DETECTION ###
###                 ###
#######################
input("Waiting. Press Enter to take Color ID Value")
"""The color sensor has several modes to detect colors, here are two useful ones"""

"""
{ID mode} uses a built-in detection function, and gives you a color name
(e.g. "red", "orange", "violet")
* very quick and simple
* but not exactly reliable
* often wrong

Returns "unknown" when facing an error, or an unkown color
"""
color_name = color.get_color_name()
print(color_name)

input("Waiting. Press Enter to take Color Component Data")
"""
{Component mode} gives RGB values, a list of Red, Green, and Blue
* reliable, more info
* needs custom function to determine a color profile
* great for just reading one type of color

Returns a list of [None, None, None] on error
values range from 0 to 255
"""
rgb_list = color.get_rgb()
print(rgb_list)

############################
###                      ###
### ULTRASONIC DETECTION ###
###                      ###
############################
"""The Ultrasonic Sensor has two main modes, and one extra that we don't use generally"""

input("Waiting. Press Enter to take Ultrasonic CM Distance")
"""{Centimeter mode} reads the distance in centimeters. Returns a float value."""
distance = ultra.get_cm()
print(distance)

input("Waiting. Press Enter to take Ultrasonic IN Distance")
"""{Inches mode} still reads distance but gives back inches. Also a float value."""
distance = ultra.get_inches()
print(distance)

input("Waiting. Press Enter to take Ultrasonic Detection value")
"""{Detection mode} uses ultrasonic sensor to detect any other ultrasonic sensors nearby. Output boolean."""
print(ultra.detects_other_us_sensor())
