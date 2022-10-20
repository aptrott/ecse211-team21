import time

from utils.brick import Motor

motor = Motor("A")
motor.set_limits(50, 90)

if __name__ == "__main__":
    motor.reset_encoder()
    while True:
        print(motor.get_position())
        time.sleep(2)