import time
from enum import Enum

from utils.brick import Motor

DELAY = 1

class InputLever:
    
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
    IDLE = (-60, 40)
    DRUMMING_ON = (40, 90)
    EMERGENCY_STOP = (90, 300)

    def __init__(self, min_position, max_position):
        self.min_position = -max_position
        self.max_position = -min_position


def main():
    try:
        lever = InputLever(Motor("A"))
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

    except BaseException:
        exit()


if __name__ == "__main__":
    main()
