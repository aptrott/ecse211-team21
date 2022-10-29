import time
from enum import Enum
from utils.brick import Motor
from utils import sound
from utils.brick import TouchSensor

DELAY = 0.2
# Creating the 4 different sounds that will be played
# The duration and the volume for all four sounds are the same
# Obviously, each sound has a different pitch
SOUND_A = sound.Sound(duration=1, pitch="G6", volume=80)
SOUND_B = sound.Sound(duration=1, pitch="C6", volume=80)
SOUND_C = sound.Sound(duration=1, pitch="D6", volume=80)
SOUND_D = sound.Sound(duration=1, pitch="G5", volume=80)



class DrumMotor:
    """
    The DrumMotor class is responsible for the drumming mechanism that depends on the motor's rotation
    """
    # Initialization of the drumming motor and control motor
    def __init__(self, motor: Motor):
        self.motor = motor

    def drumming_on(self):
        # When the motor starts turning, the drumming mechanism starts since it depends on the motor's rotation.
        # The motor is turn on by assigning a power percentage through the set_power(power) function.
        self.motor.set_power(50)

    def drumming_off(self):
        # A motor is turned off when it does not have power to rotate. Thus, drumming is turned off.
        self.motor.set_power(0)


class InputLever:
    """
    The inputLever class is responsible for defining the state of the input mechanism defined above.
    The input is the angle position of a motor in degrees. depending on its relative position, the input can be
    either Drumming Idle, Drumming On, Emergency Stop
    """
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
        for state in LeverState:  # LeverState is an enum class that has the 3 possible states of the input lever
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
    IDLE = (-60, 40) # Idle state between -60 degrees and 40 degrees
    DRUMMING_ON = (40, 90) # Drumming_On between 40 degrees and 90 degrees
    EMERGENCY_STOP = (90, 300) # Emergency_stop between 90 degrees and 300 degrees

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
        drum = DrumMotor(Motor("C")) #initializing the drumming mechanism motor at the input port C

        # Initiating the 4 different touch sensors 
        TOUCH_SENSOR_A = TouchSensor(1) # Touch Sensor A initialization at port 1
        TOUCH_SENSOR_B = TouchSensor(2) # Touch Sensor B initialization at port 2
        TOUCH_SENSOR_C = TouchSensor(3) # Touch Sensor C initialization at port 3
        TOUCH_SENSOR_D = TouchSensor(4) # Touch Sensor D initialization at port 4


        #To make sure that the starting angle is always the same; because all other angle measurements will be relative
        #to the starting position
        print("To start the program, ensure that you move the input lever idle position")
        while not lever.has_moved(DELAY):  # Waiting for lever to be moved to initial position
            pass
        while lever.has_moved(DELAY):  # Waiting for lever to stop moving
            pass
        lever.motor.reset_encoder()  # Resetting encoder based on initial set emergency stop lever position.
        lever_state = LeverState.IDLE # The start will always be Drumming Idle state

        while True:
            print(f"{lever_state}, {lever.position}")
            sensorA = TOUCH_SENSOR_A.is_pressed()
            sensorB = TOUCH_SENSOR_B.is_pressed()
            sensorC = TOUCH_SENSOR_C.is_pressed()
            sensorD = TOUCH_SENSOR_D.is_pressed()

            if (sensorA or sensorB or sensorC or sensorD) and (lever_state is not LeverState.EMERGENCY_STOP):
                # While the lever state is NOT at the emergency stop, pressing one of the sensors will turn on the drumming
                drum.drumming_on()


                """
                4 consecutive conditional If statements to ensure that the sound is produced 
                only if one touch sensor is pressed at a time. 
                Each conditional statement is responsible for generating the sound according to the touch sensor 
                that was pressed
                """
                # Case where True/False/False/False =>  sound A is played
                if sensorA and (not sensorB) and (not sensorC) and (not sensorD):

                    print("Playing sound A")
                    SOUND_A.play()
                    SOUND_A.wait_done()

                # Case where False/True/False/False =>  sound B is played
                elif (not sensorA) and sensorB and (not sensorC) and (not sensorD):
                    print("Playing sound B")
                    SOUND_B.play()
                    SOUND_B.wait_done()

                # Case where False/False/True/False => sound C is played
                elif (not sensorA) and (not sensorB) and sensorC and (not sensorD):
                    print("Playing sound C")
                    SOUND_C.play()
                    SOUND_C.wait_done()

                # Case where False/False/False/True => sound D is played 
                elif (not sensorA) and (not sensorB) and (not sensorC) and sensorD:
                    print("Playing sound D")
                    SOUND_D.play()
                    SOUND_D.wait_done()

            elif lever_state is LeverState.DRUMMING_ON:
                #Checking the lever_state from the enumarion class
                drum.drumming_on()

            elif lever_state is LeverState.EMERGENCY_STOP:
                #if the lever state is at the Emergency_Stop state, then we have to exit the program
                exit()

            time.sleep(DELAY)  #

            lever_state = lever.get_state()
    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main()
