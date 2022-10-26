import time
from enum import Enum

from utils.brick import Motor
from utils import sound
from utils.brick import TouchSensor

DELAY = 0.2
# Creating the 4 different sounds that will be played 
SOUND_A = sound.Sound(duration=1, pitch="G6", volume=80)
SOUND_B = sound.Sound(duration=1, pitch="C6", volume=80)
SOUND_C = sound.Sound(duration=1, pitch="D6", volume=80)
SOUND_D = sound.Sound(duration=1, pitch="G5", volume=80)

class DrumMotor:
    # Initialization of the drumming motor and control motor

    def __init__(self, motor: Motor):
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
    IDLE = (-60, 50)
    DRUMMING_ON = (50, 120)
    EMERGENCY_STOP = (120, 300)

    def __init__(self, min_position, max_position):
        self.min_position = -max_position
        self.max_position = -min_position


def main():
    try:
        lever = InputLever(Motor("A"))
        drum = DrumMotor(Motor("C"))
        
        # Initiating the 4 different touch sensors 
        TOUCH_SENSOR_A = TouchSensor(1)
        TOUCH_SENSOR_B = TouchSensor(2)
        TOUCH_SENSOR_C = TouchSensor(3)
        TOUCH_SENSOR_D = TouchSensor(4)

        print("To start the program, ensure that you move the input lever idle position")
        while not lever.has_moved(DELAY):  # Waiting for lever to be moved to initial position
            pass
        while lever.has_moved(DELAY):  # Waiting for lever to stop moving
            pass
        lever.motor.reset_encoder()  # Resetting encoder based on initial set emergency stop lever position
        lever_state = LeverState.IDLE

        while True:
            print(f"{lever_state}, {lever.position}")
            sensorA = TOUCH_SENSOR_A.is_pressed() 
            sensorB = TOUCH_SENSOR_B.is_pressed()  
            sensorC = TOUCH_SENSOR_C.is_pressed()  
            sensorD = TOUCH_SENSOR_D.is_pressed() 


            if (sensorA or sensorB or sensorC or sensorD) and (lever_state is not LeverState.EMERGENCY_STOP):
               
                drum.drumming_on()
               
                if sensorA == True and sensorB == False and sensorC == False and sensorD == False: 
                  print("Playing sound A") 
                  SOUND_A.play()
                  SOUND_A.wait_done()

               # Case where False/True/False/False =>  sound B is played 
                elif sensorA == False and sensorB == True and sensorC == False and sensorD == False: 
                  print("Playing sound B")
                  SOUND_B.play()
                  SOUND_B.wait_done()

               # Case where False/False/True/False => sound C is played 
                elif sensorA == False and sensorB == False and sensorC == True and sensorD == False: 
                  print("Playing sound C")
                  SOUND_C.play()
                  SOUND_C.wait_done()

                # Case where False/False/False/True => sound D is played 
                elif sensorA == False and sensorB == False and sensorC == False and sensorD == True: 
                  print("Playing sound D")
                  SOUND_D.play()
                  SOUND_D.wait_done()

            elif lever_state is LeverState.DRUMMING_ON:
                drum.drumming_on()

            elif lever_state is LeverState.EMERGENCY_STOP:
               exit()

                        
            time.sleep(DELAY)
            
            lever_state = lever.get_state()
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
      main()

