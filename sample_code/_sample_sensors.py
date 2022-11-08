"""sample_sensors

This is sensor sample code, with short explanations for each 
individual sensor that has a class in utils.brick

Author: Ryan Au
January 25th, 2022
"""

####################
### Touch Sensor ###
####################

from utils.brick import wait_ready_sensors, TouchSensor

touch = TouchSensor(1)

wait_ready_sensors() # init sensors

touch.get_raw_value() # => 0 or 1
touch.is_pressed()    # => False or True

#############################
### EV3 Ultrasonic Sensor ###
#############################

from utils.brick import wait_ready_sensors, EV3UltrasonicSensor

ultra = EV3UltrasonicSensor(2)

wait_ready_sensors()

ultra.get_raw_value() # => starts with centimeter reading

ultra.detects_other_us_sensor() # switch mode, False or True
ultra.get_cm() # switch mode, centimeter distance
ultra.get_inches() # switch mode, inches distance
ultra.get_inches() # no mode switch, it's unnecessary

########################
### EV3 Color Sensor ###
########################

from utils.brick import wait_ready_sensors, EV3ColorSensor

color = EV3ColorSensor(3)

wait_ready_sensors()

color.get_raw_value() # => returns raw value of current mode.
color.get_ambient() # => 1 float value. detects ambient light. lightbulb stays off
color.get_red() # => 1 float value. detects red light. red light turns on.
color.get_color_name() # => Use color sensor's color detection, return a string name of color
color.get_rgb() # => Returns a list of floats: [Red, Green, Blue] (excludes unknown 4th value)
color.get_raw_value() # => raw rgb value, includes "unknown 4th value"

#######################
### EV3 Gyro Sensor ###
#######################

from utils.brick import wait_ready_sensors, EV3GyroSensor

gyro = EV3GyroSensor(4)

gyro.get_raw_value() # Use the BOTH mode by default.

gyro.get_abs_measure() # => total degrees rotated. 
gyro.get_dps_measure() # => current rotation speed in degrees per second.
gyro.get_both_measure() # => list of both float values: [abs, dps]

