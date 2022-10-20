#!/usr/bin/env python3

"""
Script to deploy this project from a computer to a robot. See main entry point at the bottom for
command line arguments.
"""

from threading import Thread
from tkinter import Tk
from tkinter.ttk import Button
from types import FunctionType
import json
import os
import sys


ENV_FILE = ".env"  # in this folder
ECSE211_DIR = "/home/pi/ecse211"  # on the brick

error = lambda text: print(f"\033[91m{text}\033[0m")  # print text in red


def is_raspberry_pi() -> bool:
    "Return True if script is run on Raspberry Pi, False otherwise."
    MODEL_FILE = "/sys/firmware/devicetree/base/model"
    if os.path.isfile(MODEL_FILE):
        with open(MODEL_FILE) as f:
            return "raspberry" in f.read().lower()
    return False


def read_project_info():
    "Return the project information from the project_info.json file."
    with open("project_info.json") as f:
        return json.load(f)


def read_password():
    "Read the password from the hidden .env file, or prompt user to enter password if it does not exist."
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            f.write('{\n  "password": "ENTER YOUR BRICKPI PASSWORD HERE"\n}\n')  # change the .env file, NOT this line
        error("Robot password not set in .env file! Please enter it there, save the file, and try again.")
        exit(1)
    with open(ENV_FILE) as f:
        return json.load(f)["password"]


is_pi = is_raspberry_pi()
is_windows = os.name == "nt"
project_info = read_project_info()
robot_name = f"dpm-{project_info['group']}.local"
password = read_password()


def copy_project_folder_to_brick():
    """
    Copy this project folder to brick, under the ecse211 folder. This will overwrite previous
    versions of the project.
    """
    project_name = os.path.basename(os.getcwd())
    robot_project_path = f"{ECSE211_DIR}/{project_name}"
    
    if is_windows:
        rm_cmd = f'plink -batch -l pi -pw "{password}" {robot_name} "rm -rf {robot_project_path}"'
        if command_result(rm_cmd):
            error("Failed to connect to brick or remove old project. Please ensure the brick is turned on and "
                  "connected to the same network as this computer.")
        else:
            copy_cmd = f'pscp -batch -l pi -pw "{password}" -r {os.getcwd()} pi@{robot_name}:{ECSE211_DIR}'
    else:
        copy_cmd = f'''sshpass -p "{password}" ssh pi@{robot_name} "rm -rf {robot_project_path
            }" && sshpass -p "{password}" scp -pr "{os.getcwd()}" pi@{robot_name}:{robot_project_path}'''
    print(f"Copying {project_name} to {robot_name}...")
    if command_result(copy_cmd):
        error("Failed to copy project to brick. Please ensure it is turned on and connected to "
              "the same network as this computer.")


def run_on_brick(program_path: str, cmd: str):
    "Run a given command on the brick, using the given path as a working directory."
    if is_windows:
        run_cmd = f'plink -batch -l pi -pw "{password}" {robot_name} "cd {program_path} && {cmd}"'
    else:
        run_cmd = f'sshpass -p "{password}" ssh pi@{robot_name} "cd {program_path} && {cmd}"'
    print(f"Running command on {robot_name}:\n> {run_cmd}".replace(password, 8 * '*'))
    if command_result(run_cmd):
        error(f"Failed to run `{run_cmd}` command on brick.")


def command_result(command: str) -> int:
    "Return an integer status code, 0 if successful, non-zero otherwise."
    if is_windows:  # Windows
        return os.system(command)
    else:  # *nix
        return os.WEXITSTATUS(os.system(command))


def run_main_entry_point():
    "Run the main entry point defined in project_info.json."
    project_name = os.path.basename(os.getcwd())
    main_entry_point = project_info["entrypoint"]
    python_cmd = f"python3 {main_entry_point}"
    run_on_brick(f"{ECSE211_DIR}/{project_name}", python_cmd)


def deploy_and_run():
    "Copy project to robot then run main entry point."
    copy_project_folder_to_brick()
    run_main_entry_point()


def reset_brick():
    "Reset the brick."
    project_name = os.path.basename(os.getcwd())
    run_on_brick(f"{ECSE211_DIR}/{project_name}", "python3 scripts/reset_brick.py")


def run_in_background(action: FunctionType) -> FunctionType:
    "Use to run an action (a function) in the background."
    return Thread(target=action).start


class DeployToRobotGUI:
    "Simple window with robot deployment options."
    DELAY_MS = 100  # delay between button updates in milliseconds
    PAD_X, PAD_Y = 20, 5  # padding between window buttons in pixels

    def __init__(self, root: Tk):
        self.root = root
        root.title("Deploy to robot options")
        self.button_actions: dict[Button, FunctionType] = {
            Button(root, text="Deploy DPM Project on Robot without running"): copy_project_folder_to_brick,
            Button(root, text="Deploy and run DPM Project on Robot"): deploy_and_run,
            Button(root, text="Reset Robot"): reset_brick,
        }
        for button in self.button_actions:
            button.pack(padx=self.PAD_X, pady=self.PAD_Y)

    def update_button_actions(self):
        "Recursively update button actions to allow them to be spawned repeatedly."
        for button, action in self.button_actions.items():
            button.config(command=run_in_background(action))
        self.root.after(self.DELAY_MS, self.update_button_actions)


if __name__ == "__main__":
    "Main entry point."
    if is_pi:
        error("Run this script from a computer to deploy the codebase to your robot.")
        exit(1)

    if len(sys.argv) == 1:  # show GUI when there are no commmand line arguments
        root = Tk()
        DeployToRobotGUI(root).update_button_actions()
        root.mainloop()

    if "-copy" in sys.argv:
        copy_project_folder_to_brick()

    if "-run" in sys.argv:
        run_main_entry_point()

    if "-reset" in sys.argv:
        reset_brick()
