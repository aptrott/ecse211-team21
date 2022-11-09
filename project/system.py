# from utils.brick import Motor, TouchSensor, reset_brick, wait_ready_sensors
import time

LOOP_INTERVAL = 0.500

# wait_ready_sensors(True)

GRID_COLUMNS = 5
GRID_ROWS = 5
GRID_CELLS = GRID_COLUMNS * GRID_ROWS
MAXIMUM_CUBES = 15
GRID_CELL_SIZE = 4  # cm


class CubeGrid:

    def __init__(self, user_input):
        self.valid_binary_input = self.validate_binary_user_input(user_input)
        self.grid: dict[list] = self.process_grid()

    @staticmethod
    def validate_binary_user_input(user_input):
        if len(user_input) > GRID_CELLS:
            raise Exception(
                f'Input string is invalid, maximum length of {GRID_CELLS} exceeded ({len(user_input)} entered in total)')
        if any([character not in "01" for character in user_input]):
            raise Exception('Input string is invalid, only "1"s and "0"s are allowed')
        if user_input.count("1") > MAXIMUM_CUBES:
            raise Exception(
                f'Input string is invalid, maximum of {MAXIMUM_CUBES} "1"s exceeded ({user_input.count("1")} entered in total)')
        return user_input.ljust(GRID_CELLS, '0')

    def process_grid(self):
        grid = {k: [] for k in iter(range(1, GRID_COLUMNS + 1))}
        for i, bit in enumerate(self.valid_binary_input):
            column = (i % GRID_COLUMNS) + 1
            if bit == "1":
                row = GRID_ROWS - (i // GRID_ROWS)
                row_list = grid.get(column)
                row_list.append(row)
                grid[column] = row_list
        return grid

    def get_cube_row_position(self, row):
        return self.grid.get(row)

    def preview_grid(self):
        output = "-----------\n"
        for row in range(GRID_ROWS, 0, -1):
            output += "|"
            for column in self.grid:
                if row in self.grid[column]:
                    output += "#|"
                else:
                    output += " |"
            output += "\n"
        output += "-----------\n"
        print(output)


def get_keyboard_binary_user_input():
    input_string = str(input(
        f'Enter a string of "1"s and "0"s maximum length {GRID_CELLS}, containing a maximum of {MAXIMUM_CUBES} "1"s:\n'))
    return input_string.replace(" ", "")


if __name__ == "__main__":
    try:
        while True:
            try:
                cube_grid = CubeGrid(get_keyboard_binary_user_input())
                print(
                    f'{cube_grid.valid_binary_input} ({cube_grid.valid_binary_input.count("1")} cubes required)')
                print(cube_grid.grid)
                cube_grid.preview_grid()

            except Exception as e:
                print(e)

            time.sleep(LOOP_INTERVAL)

    except KeyboardInterrupt:
        # reset_brick()
        exit(0)
