import math
import time

from utils.brick import Motor
from utils import sound
from utils.brick import TouchSensor

class Pushing_piston:
    # Initialization of the motor

    def __init__(self, motor: Motor):
        self.motor = motor

    def getAngle(self, row, radius):
        # setting 50% power to the motor in order to turn it on
        #self.motor.set_power(50)
        linear_distance = 4*row-0.5
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle


    def push(self,row):
        # setting 50% power to the motor in order to turn it on
        rotation_angle = self.getAngle(row)
        self.motor.set_power(50)
        self.motor.set_position_relative(rotation_angle)
        time.sleep(2)
        self.motor.set_position_relative(-rotation_angle)

    




