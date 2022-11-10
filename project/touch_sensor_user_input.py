#!/usr/bin/env python3

"""
Module to play sounds when the touch sensor is pressed.
This file must be run on the robot.
"""

from utils import sound
from utils.brick import TouchSensor, wait_ready_sensors

import time

# Creating the 2 different to be played at each input.
# each sound will confirm to the user whether they input '1' or '0'
SOUND_1_ = sound.Sound(duration=1, pitch="G6", volume=50)
SOUND_0_ = sound.Sound(duration=1, pitch="C6", volume=50)
# Initiating the 2 different touch sensors for the two possible inputs '1' and '0'
TOUCH_SENSOR_1_ = TouchSensor(1)
TOUCH_SENSOR_0_ = TouchSensor(2)
TOUCH_SENSOR_ready_ = TouchSensor(3)

input_max = 25  # this will be the maximum input expected according to our grid size


def get_touch_sensor_binary_user_input():
    input_counter = 0  # This will be a counter that will check how many times did the user input with the sensors
    user_input_sense = ""
    while input_counter < input_max and not TOUCH_SENSOR_ready_.is_pressed():
        if TOUCH_SENSOR_1_.is_pressed() and not TOUCH_SENSOR_0_.is_pressed():
            user_input_sense += "1"
            input_counter += 1
            SOUND_1_.play()
            SOUND_1_.wait_done()
        if TOUCH_SENSOR_0_.is_pressed() and not TOUCH_SENSOR_1_.is_pressed():
            user_input_sense += "0"
            input_counter += 1
            SOUND_0_.play()
            SOUND_0_.wait_done()
    return user_input_sense



