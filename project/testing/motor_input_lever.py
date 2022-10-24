import time
from enum import Enum

from utils.brick import Motor


class InputLever:
    """
    class InputLever.
    The main purpose of this class to read the current position of the motor.
    The current position of the motor will be used as an input to decide between:
        1- Emergency stop (rotate between 0 degree and 119 degrees)
        2- Stop drumming (rotate between 120 degrees and 239 degrees)
        3- Start drumming (rotate between 240 degrees 360 degrees)
    """

    def __init__(self, motor: Motor):
        """
        The class constructor takes the motor as an input.
        """
        self.motor = motor

    @property
    def position(self):
        return self.motor.get_position()

    def get_state(self):
        for state in LeverState:
            if self.position in range(state.min_position, state.max_position):
                return state
        return None

    def has_moved(self, delay):
        last_position = self.motor.get_position()
        time.sleep(delay)
        current_position = self.motor.get_position()
        return last_position != current_position


class LeverState(Enum):
    IDLE = (-60, 50)
    DRUMMING_ON = (50, 120)
    EMERGENCY_STOP = (120, 300)

    def __init__(self, min_position, max_position):
        self.min_position = -max_position
        self.max_position = -min_position


def main():
    try:
        print("To start the program, ensure that you move the input lever idle position")
        while not lever.has_moved(DELAY):  # Waiting for lever to be moved to initial position
            pass
        while lever.has_moved(DELAY):  # Waiting for lever to stop moving
            pass
        lever.motor.reset_encoder()  # Resetting encoder based on initial set emergency stop lever position
        lever_state = LeverState.IDLE

        while True:
            print(f"{lever_state}, {lever.position}")
            time.sleep(DELAY)
            lever_state = lever.get_state()

    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    DELAY = 0.2

    lever = InputLever(Motor("A"))

    main()
