from utils.brick import EV3UltrasonicSensor, reset_brick, wait_ready_sensors
import time

ultra = EV3UltrasonicSensor(1) # PORT 1
LOOP_INTERVAL = 0.500

wait_ready_sensors(True)

try:
    while True:
        v = ultra.get_value()
        if v != None:
            print(v)
        time.sleep(LOOP_INTERVAL)
except KeyboardInterrupt:
    reset_brick()
    exit(0)
