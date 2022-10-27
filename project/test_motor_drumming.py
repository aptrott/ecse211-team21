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
        self.motor.set_power(50)

    def drumming_off(self):
        self.motor.set_power(0)

def main():
     try:
          drum = DrumMotor(Motor("C"))
        
          # Initiating the 4 different touch sensors 
          TOUCH_SENSOR_A = TouchSensor(1)

          drumming = False
          while True:
          
               if TOUCH_SENSOR_A.is_pressed():
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
          exit()


if __name__ == "__main__":
      main()



