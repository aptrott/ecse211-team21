# from utils.brick import Motor, TouchSensor, reset_brick, wait_ready_sensors
import time

LOOP_INTERVAL = 0.500

# wait_ready_sensors(True)

GRID_COLUMNS = 5
GRID_ROWS = 5
GRID_CELLS = GRID_COLUMNS * GRID_ROWS
GRID_CELL_WIDTH = 4  # cm
GRID_CELL_HEIGHT = 4  # cm


def get_keyboard_binary_input_string():
    max_length = GRID_CELLS
    max_ones = 15
    input_string = str(input(
        f'Enter a string of "1"s and "0"s maximum length {max_length}, containing a maximum of {max_ones} "1"s:\n'))
    input_string = input_string.replace(" ", "")
    return validate_binary_input_string(input_string, max_length, max_ones)


def validate_binary_input_string(input_string, max_length, max_ones):
    if len(input_string) > max_length:
        raise Exception(
            f'Input string is invalid, maximum length of {max_length} exceeded ({len(input_string)} entered in total)')
    if any([character not in "01" for character in input_string]):
        raise Exception('Input string is invalid, only "1"s and "0"s are allowed')
    if input_string.count("1") > max_ones:
        raise Exception(
            f'Input string is invalid, maximum of {max_ones} "1"s exceeded ({input_string.count("1")} entered in total)')
    return input_string.ljust(max_length, '0')


def process_binary_input_string(binary_input_string):
    grid = {k: [] for k in iter(range(1, GRID_COLUMNS + 1))}
    for i, bit in enumerate(binary_input_string):
        column = i % GRID_COLUMNS + 1
        if bit == "1":
            row = GRID_ROWS - (i // GRID_ROWS)
            row_list = grid.get(column)
            row_list.append(row)
            grid.update({column: row_list})
    return grid


def preview_grid(grid):
    output = "-----------\n"
    for row in range(GRID_ROWS, 0, -1):
        output += "|"
        for column in grid:
            if row in grid[column]:
                output += "#|"
            else:
                output += " |"
        output += "\n"
    output += "-----------\n"
    return output


if __name__ == "__main__":
    try:
        while True:
            try:
                s = get_keyboard_binary_input_string()
                print(f'{s} ({s.count("1")} cubes required in total)')
                g = process_binary_input_string(s)
                print(g)
                p = preview_grid(g)
                print(p)
            except Exception as e:
                print(e)

            time.sleep(LOOP_INTERVAL)

    except KeyboardInterrupt:
        # reset_brick()
        exit(0)
