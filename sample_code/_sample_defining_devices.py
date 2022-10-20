"""sample_defining_devices

Shows 3 different methods of declaring devices for a BrickPi.
(1) configure_ports - one method call for all devices. Can become a long line.
(2) create_motors & configure_ports - one for sensors, one for motors
(3) Individual initialization & wait_ready_sensors - recommended (for debugging purposes)

Any of these three methods should be completely valid.

Author: Ryan Au
January 24th, 2022
"""

### This file should be moved to the project/ folder if you want to run it ### 
from utils.brick import configure_ports, TouchSensor, EV3ColorSensor, EV3UltrasonicSensor, EV3GyroSensor, Motor, wait_ready_sensors

###################################################### Method 1

T_SENSOR, C_SENSOR, US_SENSOR, G_SENSOR, MOTOR1, MOTOR2, MOTOR3 = configure_ports(
    PORT_1=TouchSensor, PORT_2=EV3ColorSensor, PORT_3=EV3UltrasonicSensor, PORT_4=EV3GyroSensor, PORT_A=Motor, PORT_B=Motor, PORT_C=Motor)

###################################################### Method 2

M1, M2, M3 = Motor.create_motors("ABC")
T_SENSOR, C_SENSOR, US_SENSOR, G_SENSOR = configure_ports(
    PORT_1=TouchSensor, PORT_2=EV3ColorSensor, PORT_3=EV3UltrasonicSensor, PORT_4=EV3GyroSensor)

###################################################### Method 3

T_SENSOR, C_SENSOR = TouchSensor(1), EV3ColorSensor(2)
US_SENSOR, G_SENSOR = EV3UltrasonicSensor(3), EV3GyroSensor(4)
M1, M2, M3 = Motor('A'), Motor('B'), Motor('C')

wait_ready_sensors() # wait for initialization of sensors
# wait_ready_sensors(True) # Give value True as argument to print out which sensors are being initialized
