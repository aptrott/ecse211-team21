from cgi import print_arguments
from distutils.log import error
from time import sleep
import time
from utils import sound
from utils.brick import  wait_ready_sensors,Motor
# Initialization of the drumming motor and control motor
DELAY_SEC = 0.05
drum_motor =Motor("A")
control_motor=Motor("B")
drum_motor.reset_encoder #get the current position in degree,0 at the start
control_motor.reset_encoder#get the current position in degree,0 at the start
time.sleep(2) #wait for the initialization to finish
wait_ready_sensors() # Note: Touch sensors actually have no initialization time

def  drum_motor_init():
    try:
        if(control_motor.get_position<90)and(control_motor.get_position>10):
          drum_motor.set_power(40)
        else:
            print ("Please turn on the switch")
  
    except IOError as error:
      print (error)  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        

def drum_on_switch_on():
    "In an infinite loop, play a single note when the touch sensor is pressed."
    try:
        while True:
            if (control_motor.get_position>90)or(control_motor.get_position<10):
                 drum_motor.set_power(0)
                 exit()
                 
            
    except BaseException:  # capture all exceptions including KeyboardInterrupt (Ctrl-C)
        exit()


if __name__ == '__main__':
   drum_motor_init
   time.sleep(4)
   drum_on_switch_on