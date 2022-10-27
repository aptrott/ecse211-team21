#!/usr/bin/env python3

"""
Module to play sounds when the touch sensor is pressed.
This file must be run on the robot.
"""
 
from utils import sound
from utils.brick import TouchSensor, wait_ready_sensors
import time 

# Creating the 4 different sounds that will be played 
SOUND_A = sound.Sound(duration=1, pitch="G6", volume=50)
SOUND_B = sound.Sound(duration=1, pitch="C6", volume=50)
SOUND_C = sound.Sound(duration=1, pitch="D6", volume=50)
SOUND_D = sound.Sound(duration=1, pitch="G5", volume=50)

# Initiating the 4 different touch sensors 
TOUCH_SENSOR_A = TouchSensor(1)
TOUCH_SENSOR_B = TouchSensor(2)
TOUCH_SENSOR_C = TouchSensor(3)
TOUCH_SENSOR_D = TouchSensor(4)

wait_ready_sensors() # Note: Touch sensors actually have no initialization time

def play_sound_on_button_press():

    "In an infinite loop, play a single note when the touch sensor is pressed."
    try:
        while (True):
            # Case where True/False/False/False => sound A is played 
            if TOUCH_SENSOR_A.is_pressed() == True and TOUCH_SENSOR_B.is_pressed() == False and TOUCH_SENSOR_C.is_pressed() == False and TOUCH_SENSOR_D.is_pressed() == False: 
                print("Playing sound A") 
                SOUND_A.play()
                SOUND_A.wait_done()

            # Case where False/True/False/False =>  sound B is played 
            elif TOUCH_SENSOR_A.is_pressed() == False and TOUCH_SENSOR_B.is_pressed() == True and TOUCH_SENSOR_C.is_pressed() == False and TOUCH_SENSOR_D.is_pressed() == False: 
                print("Playing sound B")
                SOUND_B.play()
                SOUND_B.wait_done()

            # Case where False/False/True/False => sound C is played 
            elif TOUCH_SENSOR_A.is_pressed() == False and TOUCH_SENSOR_B.is_pressed() == False and TOUCH_SENSOR_C.is_pressed() == True and TOUCH_SENSOR_D.is_pressed() == False: 
                print("Playing sound C")
                SOUND_C.play()
                SOUND_C.wait_done()

           # Case where False/False/False/True => sound D is played 
            elif TOUCH_SENSOR_A.is_pressed() == False and TOUCH_SENSOR_B.is_pressed() == False and TOUCH_SENSOR_C.is_pressed() == False and TOUCH_SENSOR_D.is_pressed() == True: 
                print("Playing sound D")
                SOUND_D.play()
                SOUND_D.wait_done()

            time.sleep(0.05) 

    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        exit()

if __name__ == '__main__':
    play_sound_on_button_press()