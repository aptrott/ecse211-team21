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
        output = "\u0332 "*16 + "\n"
        for row in range(GRID_ROWS, 0, -1):
            output += "|"
            for column in self.grid:
                if row in self.get_cubes_in_column(column):
                    output += "\u2588\u2588|"
                else:
                    output += "  |"
            output += "\n"
        output += "\u203E"*16
        print(output)


def get_keyboard_binary_user_input():
    input_string = str(input(
        f'\nEnter a string of "1"s and "0"s maximum length {GRID_CELLS}, containing a maximum of {MAXIMUM_CUBES} "1"s:\n'))
    return input_string.replace(" ", "")


if __name__ == "__main__":
    try:
        while True:
            try:
                keyboard_input = get_keyboard_binary_user_input()
                cube_grid = CubeGrid(keyboard_input)
                print(
                    f'{cube_grid.valid_binary_input} ({cube_grid.valid_binary_input.count("1")} cubes required)')
                print(cube_grid.grid)
                cube_grid.preview_grid()
                for cube in cube_grid:
                    print(cube, end=" ")
                print()

            except Exception as e:
                print(e)

            time.sleep(LOOP_INTERVAL)

    except KeyboardInterrupt:
        # reset_brick()
        exit(0)
