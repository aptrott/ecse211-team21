import math
import time

from utils.brick import Motor, reset_brick
from utils import sound
from utils.brick import TouchSensor

LOOP_INTERVAL = 0.050


class Pushing_piston:
    # Initialization of the motor

    def __init__(self, motor: Motor):
        self.motor = motor
        self.motor.set_limits(dps=180)

    def get_rotation_angle(self, linear_distance):
        radius = 1.95
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle

    def push(self, row):
        distance = 4 * row - 0.5
        rotation_angle = self.get_rotation_angle(distance)
        self.motor.set_position_relative(-rotation_angle)
        self.motor.wait_is_moving()
        self.motor.wait_is_stopped()
        self.motor.set_position_relative(rotation_angle)
        self.motor.wait_is_moving()
        self.motor.wait_is_stopped()

    def load_cube(self):
        distance = 3
        rotation_angle = self.get_rotation_angle(distance)
        self.motor.set_position_relative(rotation_angle)
        self.motor.wait_is_moving()
        self.motor.wait_is_stopped()
        time.sleep(2)
        self.motor.set_position_relative(-rotation_angle)
        self.motor.wait_is_moving()
        self.motor.wait_is_stopped()
        time.sleep(2)


if __name__ == "__main__":
    pushing_motor = Pushing_piston(Motor("A"))
    try:
        row = 3
        pushing_motor.load_cube()
        pushing_motor.push(row)

    except KeyboardInterrupt:
        reset_brick()
        exit()
