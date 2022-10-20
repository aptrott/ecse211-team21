#!/usr/bin/env python3

"""
Script to reset brick.
"""

import brickpi3
import os

def is_raspberry_pi() -> bool:
    "Return True if script is run on Raspberry Pi, False otherwise."
    MODEL_FILE = "/sys/firmware/devicetree/base/model"
    if os.path.isfile(MODEL_FILE):
        with open(MODEL_FILE) as f:
            contents = f.read()
            return "raspberry" in contents.lower()
    return False


def reset_brick():
    "Reset the brick hardware."
    brickpi3.BrickPi3().reset_all()
    os.system("kill -INT `cat ~/brickpi3_pid`")


if __name__ == "__main__":
    "Main entry point."
    if is_raspberry_pi():
        reset_brick()
    else:
        print("Run this script from the brick to reset its hardware.")
        exit(1)


