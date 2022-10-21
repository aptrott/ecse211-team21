import time
from enum import Enum

from utils.brick import Motor


class DrumMotor:
# Initialization of the drumming motor and control motor

     def __init__ (self, motor: Motor):
       self.motor = motor

     def drumming_on(self):
          self.motor.set_power(50)
     def drumming_off(self):
          self.motor.set_power(0)




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
    EMERGENCY_STOP = (-130,-70 )
   # DRUMMING_OFF = (-34, 20)
    DRUMMING_ON = (11, 130)
    IDLE=(-69,10)

    def __init__(self, min_position, max_position):
        self.min_position = min_position
        self.max_position = max_position


if __name__ == "__main__":
    DELAY = 0.2

    lever = InputLever(Motor("A"))
    drum  = DrumMotor(Motor("C"))

    try:
        print("To start the program, ensure that you move the input lever to the emergency stop position")
        while not lever.has_moved(DELAY):  # Waiting for lever to be moved to initial position
            pass
        while lever.has_moved(DELAY):  # Waiting for lever to stop moving
            pass
        lever.motor.reset_encoder()  # Resetting encoder based on initial set emergency stop lever position
        lever_state = LeverState.IDLE

        print("start")
        while(True):
            print(lever_state)
            if(lever_state==LeverState.DRUMMING_ON):
                drum.drumming_on()
                time.sleep(DELAY)      

            elif (lever_state==LeverState.EMERGENCY_STOP):
                drum.drumming_off()
                time.sleep(DELAY)      
            else:
                 pass
                
            lever_state = lever.get_state()

    except BaseException:
         print(BaseException)
         exit()
