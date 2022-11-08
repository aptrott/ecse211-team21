# DPM Project Flexible Setup

**Note:** If you prefer a simpler setup, please use the first option
provided in the [`README.md`](README.md) file.
If you need help with NoMachine, contact your mentor TA for assistance.
If you still have issues, you can follow the steps below.

## Instructions

0. Make sure you have setup the robot as described in the
**Getting Started Guide**.
1. If you are using **Linux** or **macOS**, install `sshpass`.
   If you are using **Windows**, install
   [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html).
   These tools allow you to send data (such as code) and commands (eg, reset)
   to the robot without entering your password every time.
2. If you are using **Windows**, install [`git`](https://git-scm.com/downloads).
   Optionally, install a GUI tool for git (eg,
   [GitHub Desktop](https://desktop.github.com/) or
   [GitKraken](https://www.gitkraken.com/)) if you do not want to use the
    command line.
3. Install an IDE that supports Python on your computer if needed.
   We recommend [Microsoft Visual Studio Code](https://code.visualstudio.com/)
   (referred to as "VS Code" from now on).
4. Open this folder (where this file is) in VS Code.
5. Enter your group number in the `project_info.json` file.
6. Allow your computer to connect to the robot by running this command (replace `xx` with your group number):

   ```bash
   ssh pi@dpm-xx.local
   ```

   You will be presented with this message:

   ```
   The authenticity of host 'dpm-xx.local (192.168.50.5)' can't be established.
   ECDSA key fingerprint is SHA256:...
   Are you sure you want to continue connecting (yes/no/[fingerprint])?
   ```

   Type `yes` and press Enter to establish the connection, then enter your password.
   It will not appear on your screen.
7. Run the `deploy_to_robot.py` script to perform any of the following actions:
   - Deploy DPM Project on Robot without running: copy this folder to the robot.
   - Deploy and run DPM Project on Robot: copy this folder to the robot
   and run the file specified in `project_info.json`.
   - Reset Robot: reset the robot.

   The first time you run this script, it will ask you to enter your 
   password in the `.env` file. After entering your password there, you
   will be able to use the above actions without re-entering it.
