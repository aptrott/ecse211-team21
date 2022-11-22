import math

from utils.brick import Motor, TouchSensor, reset_brick, wait_ready_sensors
from utils import sound
import time
import threading

LOOP_INTERVAL = 0.050

SLEEP = 1

# wait_ready_sensors(True)

GRID_COLUMNS = 5
GRID_ROWS = 5
GRID_CELLS = GRID_COLUMNS * GRID_ROWS
MAXIMUM_CUBES = 15
GRID_CELL_SIZE = 4  # cm

# Creating the 3 different to be played at each input.
# each sound will confirm to the user whether they input '1' or '0' or 'complete'
SOUND_1 = sound.Sound(duration=0.3, pitch="G6", volume=50)
SOUND_0 = sound.Sound(duration=0.3, pitch="C6", volume=50)
SOUND_COMPLETE = sound.Sound(duration=0.3, pitch="D6", volume=50)
SOUND_INVALID = sound.Sound(duration=0.3, pitch="G5", volume=50)
# Initiating the 2 different touch sensors for the two possible inputs '1' and '0'
TS_1 = TouchSensor(4)
TS_0 = TouchSensor(3)
TS_COMPLETE = TouchSensor(2)


class GridInputValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class CubeGrid:
    def __init__(self, user_input):
        self.valid_binary_input = self.__validate_binary_user_input(user_input)
        self.grid = self.__process_grid()

    def get_cubes_in_column(self, cube_column):
        return self.grid.get(cube_column)

    @staticmethod
    def get_cube_position(current_cube):
        return current_cube * GRID_CELL_SIZE

    @staticmethod
    def __validate_binary_user_input(user_input):
        if len(user_input) > GRID_CELLS:
            raise GridInputValidationError(
                f'Input string is invalid, maximum length of {GRID_CELLS} exceeded ({len(user_input)} entered in total)')
        if any([character not in "01" for character in user_input]):
            raise GridInputValidationError('Input string is invalid, only "1"s and "0"s are allowed')
        if user_input.count("1") > MAXIMUM_CUBES:
            raise GridInputValidationError(
                f'Input string is invalid, maximum of {MAXIMUM_CUBES} "1"s exceeded ({user_input.count("1")} entered in total)')
        return user_input.ljust(GRID_CELLS, '0')

    def __process_grid(self):
        grid = {k: [] for k in iter(range(1, GRID_COLUMNS + 1))}
        for index, bit in enumerate(self.valid_binary_input):
            if bit == "1":
                column = (index % GRID_COLUMNS) + 1
                row = GRID_ROWS - (index // GRID_ROWS)
                row_list = grid.get(column)
                row_list.append(row)
                grid[column] = row_list
        return grid

    def preview_grid(self):
        output = "_" * 16 + "\n"
        for row in range(GRID_ROWS, 0, -1):
            output += "|"
            for column in self.grid:
                if row in self.get_cubes_in_column(column):
                    output += "\u2588\u2588|"
                else:
                    output += "  |"
            output += "\n"
        output += "\u203E" * 16
        print(output)


class UserInput:
    def __init__(self):
        self.raw_user_input = ""
        self.is_input_complete = False
        self.is_using_touch_sensor_input = False

    def get_binary_user_input(self):
        keyboard_input_thread = threading.Thread(target=self.__get_keyboard_binary_user_input, daemon=True)
        keyboard_input_thread.start()
        self.__get_touch_sensor_binary_user_input()
        return self.raw_user_input

    def __get_keyboard_binary_user_input(self):
        user_input = str(input(
            f'Enter a string of "1"s and "0"s maximum length {GRID_CELLS}, containing a maximum of {MAXIMUM_CUBES} "1"s:\n'))
        if not self.is_using_touch_sensor_input:
            self.raw_user_input = user_input.replace(" ", "")
            self.is_input_complete = True

    @staticmethod
    def __wait_until_touch_sensor_released(touch_sensor):
        while touch_sensor.is_pressed():
            pass

    def __get_touch_sensor_binary_user_input(self):
        while not self.is_input_complete:
            time.sleep(LOOP_INTERVAL)
            if TS_0.is_pressed() or TS_1.is_pressed() or TS_COMPLETE.is_pressed():
                self.is_using_touch_sensor_input = True
            if TS_1.is_pressed() and not TS_0.is_pressed() and not TS_COMPLETE.is_pressed():
                self.raw_user_input += "1"
                SOUND_1.play()
                self.__wait_until_touch_sensor_released(TS_1)
                SOUND_1.wait_done()
            if TS_0.is_pressed() and not TS_1.is_pressed() and not TS_COMPLETE.is_pressed():
                self.raw_user_input += "0"
                SOUND_0.play()
                self.__wait_until_touch_sensor_released(TS_0)
                SOUND_0.wait_done()
            if self.is_using_touch_sensor_input:
                print(" " * 100, end="\r", flush=True)
                print(f"\r{self.raw_user_input}", end="\r", flush=True)
            if TS_COMPLETE.is_pressed() and not TS_1.is_pressed() and not TS_0.is_pressed():
                self.is_input_complete = True
                self.__wait_until_touch_sensor_released(TS_COMPLETE)
                SOUND_COMPLETE.play()
                SOUND_COMPLETE.wait_done()
                print()


class RobotMovement:
    # Initialization of the motor

    def __init__(self, motor: Motor, motor_2: Motor):
        self.initial_column = 1
        self.motor = motor
        self.motor_2 = motor_2
        self.motor.set_limits(dps=100)
        self.motor_2.set_limits(dps=100)
        self.current_column = self.initial_column

    @staticmethod
    def get_rotation_angle(linear_distance):
        radius = 2.00
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle

    def move(self, column):
        self.motor.reset_encoder()
        distance = 4 * (column - self.current_column)
        angle = self.get_rotation_angle(distance)
        self.motor.set_position_relative(angle)
        self.motor_2.set_position_relative(angle)
        time.sleep(SLEEP)
        self.motor.wait_is_stopped()
        self.motor_2.wait_is_stopped()
        self.current_column = column

    def return_to_initial(self):
        self.motor.reset_encoder()
        distance = 4 * (self.current_column - self.initial_column)
        angle = -self.get_rotation_angle(distance)
        self.motor.set_position_relative(angle)
        self.motor_2.set_position_relative(angle)
        time.sleep(SLEEP)
        self.motor.wait_is_stopped()
        self.motor_2.wait_is_stopped()
        self.current_column = self.initial_column


class Pusher:
    # Initialization of the motor

    def __init__(self, motor: Motor):
        self.motor = motor
        self.motor.set_limits(dps=360)

    @staticmethod
    def get_rotation_angle(linear_distance):
        radius = 2.05
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle

    def push(self, row):
        distance = (4 * row) - 1.5
        self.motor.reset_encoder()
        print("pushing...")
        rotation_angle = self.get_rotation_angle(distance)
        self.motor.set_position_relative(-rotation_angle)
        time.sleep(SLEEP)
        self.motor.wait_is_stopped()
        print("moving back...")
        self.motor.set_position_relative(rotation_angle)
        time.sleep(SLEEP)
        self.motor.wait_is_stopped()

    def load_cube(self):
        distance = 6
        self.motor.reset_encoder()
        rotation_angle = self.get_rotation_angle(distance)
        self.motor.set_position_relative(rotation_angle)
        time.sleep(SLEEP)
        self.motor.wait_is_stopped()
        self.motor.set_position_relative(-rotation_angle)
        time.sleep(SLEEP)
        self.motor.wait_is_stopped()


if __name__ == "__main__":
    try:
        input_string = UserInput().get_binary_user_input()
        try:
            cube_grid = CubeGrid(input_string)
        except GridInputValidationError as e:
            SOUND_INVALID.play()
            SOUND_INVALID.wait_done()
            SOUND_INVALID.play()
            SOUND_INVALID.wait_done()
            print(e)
        else:
            print(f'{cube_grid.valid_binary_input} ({cube_grid.valid_binary_input.count("1")} cubes required)')
            print(cube_grid.grid)
            cube_grid.preview_grid()

            robot_movement = RobotMovement(Motor("B"), Motor("C"))
            pusher = Pusher(Motor("D"))
            for column in cube_grid.grid:
                print(f"moving to column {column}")
                if cube_grid.get_cubes_in_column(column):
                    robot_movement.move(column)
                for cube_row in cube_grid.get_cubes_in_column(column):
                    print("loading cube")
                    pusher.load_cube()
                    print(f"pushing cube to row {cube_row}")
                    pusher.push(cube_row)
            robot_movement.return_to_initial()
            print(f"returning to initial position {robot_movement.initial_column}")

    except KeyboardInterrupt:
        # reset_brick()
        exit(0)
