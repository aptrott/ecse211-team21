import time
from enum import Enum

from utils.brick import Motor


class InputLever:
    """
    class InputLever.
    The main purpose of this class to read the current position of the motor.
    The current position of the motor will be used as an input to decide between:
        1- Start drumming (rotate between 0 degree and 119 degrees)
        2- Stop drumming (rotate between 120 degrees and 239 degrees)
        3- Emergency stop (rotate between 240 degrees 360 degrees)
    """

    def __init__(self, motor):
        """
        The class constructor takes the motor as an input. set power to 50, set limit dps to 90
        makes a call to motor.reset_encoder
        """
        self.motor = motor
        #starting_position = motor.set_position_relative(-1 * motor.get_position())  # The idea here is that we always have the same starting position for the motor.
        motor.reset_encoder()

    def get_switch_state(self):
        position = self.motor.get_position()
        if position in range(LeverStates.DrummingOn.min_position, LeverStates.DrummingOn.max_position):
            return LeverStates.DrummingOn


class LeverStates(Enum):
    DrummingOn = (0, 119)
    DrummingOff = (120, 239)
    EmergencyStop = (240, 359)

    def __init__(self, min_position, max_position):
        self.min_position = min_position
        self.max_position = max_position


if __name__ == "__main__":
    input_motor = Motor("A")
    lever = InputLever(input_motor)
    while True:
        try:
            print(lever.get_switch_state())
        except BaseException:
            quit()
