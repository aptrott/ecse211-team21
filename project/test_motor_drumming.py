from socket import if_indextoname
import time
from enum import Enum

from utils.brick import Motor
from utils import sound
from utils.brick import TouchSensor

DELAY = 0.2
class DrumMotor:
    # Initialization of the drumming motor and control motor

    def __init__(self, motor: Motor):
        self.motor = motor

    def drumming_on(self):
        # setting 50% power to the motor in order to turn it on
        self.motor.set_power(50)

    def drumming_off(self):
        # setting 0% power to the motor to turn it off
        self.motor.set_power(0)

def main():

     try:
          drum = DrumMotor(Motor("C"))  # a DrumMotor object 'drum' initialized at port C
        
          # Initiating the 4 different touch sensors 
          TOUCH_SENSOR_A = TouchSensor(1)

          drumming = False
          while True:
          
               if TOUCH_SENSOR_A.is_pressed():  # The main purpose of this to test the function of the inputs,
                                                # both the motor and the touch sensors.
                    if not drumming:
                         print("currently not drumming, turning on")
                         drumming = True
                         drum.drumming_on()
                    else:
                         print("currently drumming, turning off")
                         drumming = False
                         drum.drumming_off()
               
               time.sleep(DELAY)
            
     except KeyboardInterrupt:
          exit()  #exit execution when a keyboard interrupt occurs


if __name__ == "__main__":
      main()



