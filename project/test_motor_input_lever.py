import time
from enum import Enum

from utils.brick import Motor

DELAY = 1


class InputLever:

    def __init__(self, motor: Motor):
        """
        The class constructor takes the motor as an input.
        Motor initialization
        """
        self.motor = motor

    @property
    def position(self):
        """
        Returns: The motor current angle position in degrees
        """
        return -self.motor.get_position()

    def get_state(self):
        """
        Returns: The state of the motor, which represents the input. The state can be either Drumming Idle,
                Drumming On or Emergency Stop.
        """
        for state in LeverState:
            if self.position in range(state.min_position, state.max_position):
                return state
        return None

    def has_moved(self, delay):
        """

        Args:
            delay: time in seconds to delay between reading the last position and new current position if there
                    are any changes

        Returns: A boolean True if the motor has moved. A boolean false if the motor has not moved

        """
        last_position = self.motor.get_position()
        time.sleep(delay)
        current_position = self.motor.get_position()
        return last_position != current_position


class LeverState(Enum):
    """
    Enumeration class that includes the three possible states of the input lever motor, who changes the drumming mechanism
    accordingly.
    """
    IDLE = (-60, 40)
    DRUMMING_ON = (40, 90)
    EMERGENCY_STOP = (90, 300)

    def __init__(self, min_position, max_position):
        """

        Args:
            min_position: The least angle position for the motor at a given state A
            max_position: The most angle position for the motor at a given state A
        """
        self.min_position = min_position
        self.max_position = max_position


def main():
    try:
        lever = InputLever(Motor("A")) #initializing the input lever motor at the input port A
        print("To start the program, ensure that you move the input lever idle position")
        while not lever.has_moved(DELAY):  # Waiting for lever to be moved to initial position
            pass
        while lever.has_moved(DELAY):  # Waiting for lever to stop moving
            pass
        lever.motor.reset_encoder()  # Resetting encoder based on initial set emergency stop lever position
        lever_state = LeverState.IDLE   # Putting the lever state on IDLE

        while True:
            print(f"{lever_state}, {lever.position}")
            time.sleep(DELAY)
            lever_state = lever.get_state() #getting the state of the lever.

    except BaseException:
        exit()


if __name__ == "__main__":
    main()
