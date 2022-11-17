import math
import time

from utils.brick import Motor, reset_brick

LOOP_INTERVAL = 0.050


class RobotMovement:
    # Initialization of the motor

    def __init__(self, motor: Motor):
        self.initial_column = 0
        self.motor = motor
        self.motor.set_limits(dps=90)
        self.current_column = self.initial_column

    @staticmethod
    def get_rotation_angle(linear_distance):
        radius = 1.95
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle

    def move(self, column):
        distance = 4 * (column - self.current_column)
        self.motor.set_position_relative(self.get_rotation_angle(distance))
        self.motor.wait_is_moving()
        self.motor.wait_is_stopped()
        self.current_column = column

    def return_to_initial(self):
        distance = 4 * self.current_column - 0.5
        self.motor.set_position_relative(-self.get_rotation_angle(distance))
        self.motor.wait_is_moving()
        self.motor.wait_is_stopped()
        self.current_column = self.initial_column


if __name__ == "__main__":

    try:
        robot_movement = RobotMovement(Motor("B"))
        for c in range(1, 6):
            robot_movement.move(c)
            print(f"moving to column {c}")
            time.sleep(0.5)
        robot_movement.return_to_initial()

    except KeyboardInterrupt:
        reset_brick()
        exit()
