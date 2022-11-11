import threading
import keyboard
import time

LOOP_INTERVAL = 0.500

GRID_COLUMNS = 5
GRID_ROWS = 5
GRID_CELLS = GRID_COLUMNS * GRID_ROWS
MAXIMUM_CUBES = 15
GRID_CELL_SIZE = 4  # cm


class CubeGrid:
    def __init__(self, user_input):
        self.valid_binary_input = self.__validate_binary_user_input(user_input)
        self.grid = self.__process_grid()

    def __iter__(self):
        for cube_column in self.grid:
            for cube_row in self.get_cubes_in_column(cube_column):
                yield cube_column, cube_row

    def get_cubes_in_column(self, cube_column):
        return self.grid.get(cube_column)

    @staticmethod
    def get_cube_position(current_cube):
        return current_cube * GRID_CELL_SIZE

    @staticmethod
    def __validate_binary_user_input(user_input):
        if len(user_input) > GRID_CELLS:
            raise Exception(
                f'Input string is invalid, maximum length of {GRID_CELLS} exceeded ({len(user_input)} entered in total)')
        if any([character not in "01" for character in user_input]):
            raise Exception('Input string is invalid, only "1"s and "0"s are allowed')
        if user_input.count("1") > MAXIMUM_CUBES:
            raise Exception(
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
        output = "\u0332 " * 16 + "\n"
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

    def __get_touch_sensor_binary_user_input(self):
        while not self.is_input_complete:
            button_zero = keyboard.is_pressed("a")
            button_one = keyboard.is_pressed("s")
            button_complete = keyboard.is_pressed("d")
            if button_zero or button_one or button_complete:
                self.is_using_touch_sensor_input = True
                print(f"\r{self.raw_user_input}", end="")
            if button_complete:
                self.is_input_complete = True
                print()
                return
            if button_one and not button_zero:
                self.raw_user_input += "1"
            if button_zero and not button_one:
                self.raw_user_input += "0"
            time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    try:
        try:
            input_string = UserInput().get_binary_user_input()
            cube_grid = CubeGrid(input_string)
            print(f'{cube_grid.valid_binary_input} ({cube_grid.valid_binary_input.count("1")} cubes required)')
            print(cube_grid.grid)
            cube_grid.preview_grid()
            for cube in cube_grid:
                print(cube, end=" ")
            print()
        except Exception as e:
            print(e)

        time.sleep(LOOP_INTERVAL)

        exit(0)

    except KeyboardInterrupt:
        # reset_brick()
        exit(0)
