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
        motor.reset_encoder()

    def get_switch_state(self):
        position = self.motor.get_position()
        for state in LeverState:
            if position in range(state.min_position, state.max_position):
                return state


class LeverState(Enum):
    DRUMMING_ON = (0, 120)
    DRUMMING_OFF = (120, 240)
    EMERGENCY_STOP = (240, 360)

    def __init__(self, min_position, max_position):
        self.min_position = min_position
        self.max_position = max_position


if __name__ == "__main__":
    input_motor = Motor("A")
    lever = InputLever(input_motor)

    try:
        while True:
            print(lever.get_switch_state())
            time.sleep(0.5)

    except BaseException as e:
        exit()
