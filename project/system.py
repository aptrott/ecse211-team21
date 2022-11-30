from utils.brick import Motor, TouchSensor, reset_brick, wait_ready_sensors
from utils import sound
import math
import time
import threading

DEBUG = False

LOOP_INTERVAL = 0.050  # sec
SLEEP = 0.5  # sec

PUSH_CUBE_SPEED = 300  # dps
LOAD_CUBE_SPEED = 120  # dps
ROBOT_MOVEMENT_SPEED = 300  # dps

GRID_COLUMNS = 5
GRID_ROWS = 5
GRID_CELLS = GRID_COLUMNS * GRID_ROWS
MAXIMUM_CUBES = 15
GRID_CELL_SIZE = 4  # cm
INITIAL_PUSHER_OFFSET = 1.5  # cm

# Creating the 3 different to be played at each input.
# Each sound will confirm to the user whether they input '1' or '0' or 'complete', or if the input is invalid.
SOUND_1 = sound.Sound(duration=0.3, pitch="G6", volume=50)
SOUND_0 = sound.Sound(duration=0.3, pitch="C6", volume=50)
SOUND_COMPLETE = sound.Sound(duration=0.3, pitch="D6", volume=50)
SOUND_INVALID = sound.Sound(duration=0.3, pitch="G5", volume=50)

# Creating the 3 different touch sensors for the two possible inputs '1' and '0' 'Complete'
TOUCH_SENSOR_1 = TouchSensor(4)
TOUCH_SENSOR_0 = TouchSensor(3)
TOUCH_SENSOR_COMPLETE = TouchSensor(2)

# Creating the 3 different motors
ROBOT_MOVEMENT_MOTOR_1 = Motor("B")
ROBOT_MOVEMENT_MOTOR_2 = Motor("C")
PUSHER_MOTOR = Motor("D")

wait_ready_sensors()


class GridInputValidationError(Exception):
    """Exception for invalid grid pattern inputs."""

    def __init__(self, message):
        super().__init__(message)


class CubeGrid:
    def __init__(self, user_input):
        """This class represents the cube grid that the robot needs to produce."""
        self.valid_binary_input = self.__validate_binary_user_input(user_input)
        self.grid = self.__process_grid()

    def get_cubes_in_column(self, column):
        """This method returns a list of cubes to be placed in the given column."""
        return self.grid.get(column)

    @staticmethod
    def __validate_binary_user_input(user_input):
        """This private method validates the binary input string and pads it with 0s if it is shorter than the
        required grid. An exception is raised if the input is invalid."""
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
        """This private method uses the validated binary input string and processes it into a dictionary, with each key corresponding to a grid
        column. The value associated to each key represents a list of rows of cubes to be placed in the column."""
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
        """This method allows for a preview of the cubes on the grid to be printed to the terminal."""
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
    def __init__(self, ts_0, ts_1, ts_complete):
        """This class represents the binary user input string. Three touch sensors are used for this, as well as the terminal for keyboard input."""
        self.ts_0 = ts_0
        self.ts_1 = ts_1
        self.ts_complete = ts_complete
        self.raw_user_input = ""
        self.is_input_complete = False
        self.is_using_touch_sensor_input = False

    def get_binary_user_input(self):
        """This method is used to get binary user input from both the keyboard and the touch sensors at the same time using threading."""
        keyboard_input_thread = threading.Thread(target=self.__get_keyboard_binary_user_input, daemon=True)
        keyboard_input_thread.start()
        self.__get_touch_sensor_binary_user_input()
        return self.raw_user_input

    def __get_keyboard_binary_user_input(self):
        """This private method is used to get binary user input from the terminal. If a touch sensor is pressed before this input is entered,
        the touch sensor input is used instead. """
        user_input = str(input(
            f'Enter a string of "1"s and "0"s maximum length {GRID_CELLS}, containing a maximum of {MAXIMUM_CUBES} "1"s:\n'))
        if not self.is_using_touch_sensor_input:
            self.raw_user_input = user_input.replace(" ", "")
            self.is_input_complete = True

    @staticmethod
    def __wait_until_touch_sensor_released(touch_sensor):
        """This private method is used to wait until a touch sensor is released until proceeding to read the following presses."""
        while touch_sensor.is_pressed():
            pass

    def __get_touch_sensor_binary_user_input(self):
        """This private method is get the binary user input from the touch sensors."""
        while not self.is_input_complete:
            time.sleep(LOOP_INTERVAL)
            if self.ts_0.is_pressed() or self.ts_1.is_pressed() or self.ts_complete.is_pressed():
                self.is_using_touch_sensor_input = True
            if self.ts_1.is_pressed() and not self.ts_0.is_pressed() and not self.ts_complete.is_pressed():
                self.raw_user_input += "1"
                SOUND_1.play()
                self.__wait_until_touch_sensor_released(self.ts_1)
                SOUND_1.wait_done()
            if self.ts_0.is_pressed() and not self.ts_1.is_pressed() and not self.ts_complete.is_pressed():
                self.raw_user_input += "0"
                SOUND_0.play()
                self.__wait_until_touch_sensor_released(self.ts_0)
                SOUND_0.wait_done()
            if self.is_using_touch_sensor_input:
                print(" " * 100, end="\r", flush=True)
                print(f"\r{self.raw_user_input}", end="\r", flush=True)
            if self.ts_complete.is_pressed() and not self.ts_1.is_pressed() and not self.ts_0.is_pressed():
                self.is_input_complete = True
                self.__wait_until_touch_sensor_released(self.ts_complete)
                SOUND_COMPLETE.play()
                SOUND_COMPLETE.wait_done()
                print()


class RobotMovement:
    def __init__(self, motor_1: Motor, motor_2: Motor):
        """This class represents robot movement for the column movement. Two motors are used for this."""
        self.initial_column = 1
        self.motor_1 = motor_1
        self.motor_2 = motor_2
        self.motor_1.set_limits(dps=ROBOT_MOVEMENT_SPEED)
        self.motor_2.set_limits(dps=ROBOT_MOVEMENT_SPEED)
        self.current_column = self.initial_column

    @staticmethod
    def get_rotation_angle(linear_distance):
        """This method returns the rotation angle calculation for a given linear distance."""
        radius = 2.00
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle

    def move(self, column):
        """This method moves the robot from the current column to the given column."""
        self.motor_1.reset_encoder()
        self.motor_2.reset_encoder()
        distance = 4 * (column - self.current_column)
        rotation_angle = self.get_rotation_angle(distance)
        self.motor_1.set_position_relative(rotation_angle)
        self.motor_2.set_position_relative(rotation_angle)
        time.sleep(((1 / ROBOT_MOVEMENT_SPEED) * rotation_angle) + SLEEP)
        self.current_column = column

    def return_to_initial(self):
        """This method moves the robot back to it's initial position."""
        self.motor_1.reset_encoder()
        self.motor_2.reset_encoder()
        distance = 4 * (self.current_column - self.initial_column)
        rotation_angle = -self.get_rotation_angle(distance)
        self.motor_1.set_position_relative(rotation_angle)
        self.motor_2.set_position_relative(rotation_angle)
        time.sleep(((1 / ROBOT_MOVEMENT_SPEED) * rotation_angle) + SLEEP)
        self.current_column = self.initial_column


class Pusher:

    def __init__(self, motor: Motor):
        """This class represents the pusher for the row movement. One motor is used for this."""
        self.motor = motor

    @staticmethod
    def get_rotation_angle(linear_distance):
        """This method returns the rotation angle calculation for a given linear distance."""
        radius = 2.05
        angle = (360 * linear_distance) / (2 * math.pi * radius)
        return angle

    def push_cube(self, row):
        """This method pushes a cube to the given row."""
        self.motor.set_limits(dps=PUSH_CUBE_SPEED)
        self.motor.reset_encoder()
        distance = 4 * row
        rotation_angle = self.get_rotation_angle(distance)
        self.motor.set_position_relative(-rotation_angle)
        time.sleep(((1 / PUSH_CUBE_SPEED) * rotation_angle) + SLEEP)
        self.motor.set_position_relative(rotation_angle)
        time.sleep(((1 / PUSH_CUBE_SPEED) * rotation_angle) + SLEEP)

    def load_cube(self):
        """This method loads a cube into the pushing mechanism."""
        self.motor.set_limits(dps=LOAD_CUBE_SPEED)
        self.motor.reset_encoder()
        load_distance = 6
        ready_to_push_distance = - (load_distance - INITIAL_PUSHER_OFFSET)
        load_rotation_angle = self.get_rotation_angle(load_distance)
        ready_to_push_rotation_angle = self.get_rotation_angle(ready_to_push_distance)
        self.motor.set_position_relative(load_rotation_angle)
        time.sleep(((1 / LOAD_CUBE_SPEED) * load_rotation_angle) + SLEEP)
        self.motor.set_position_relative(ready_to_push_rotation_angle)
        time.sleep(((1 / LOAD_CUBE_SPEED) * ready_to_push_rotation_angle) + SLEEP)


if __name__ == "__main__":
    try:
        input_string = UserInput(TOUCH_SENSOR_1, TOUCH_SENSOR_0, TOUCH_SENSOR_COMPLETE).get_binary_user_input()
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

            robot_movement = RobotMovement(ROBOT_MOVEMENT_MOTOR_1, ROBOT_MOVEMENT_MOTOR_2)
            pusher = Pusher(PUSHER_MOTOR)
            for cube_column in cube_grid.grid:
                if DEBUG:
                    print(f"moving to column {cube_column}")
                if cube_grid.get_cubes_in_column(cube_column):
                    robot_movement.move(cube_column)
                for cube_row in cube_grid.get_cubes_in_column(cube_column):
                    if DEBUG:
                        print("loading cube")
                    pusher.load_cube()
                    if DEBUG:
                        print(f"pushing cube to row {cube_row}")
                    pusher.push_cube(cube_row)
            robot_movement.return_to_initial()
            if DEBUG:
                print(f"returning to initial position {robot_movement.initial_column}")
            print("Mosaic complete")

    except KeyboardInterrupt:
        reset_brick()
        exit(0)
