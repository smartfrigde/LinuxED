# LinuxSC
LinuxSC is an alternative installer for SmartCord that works on Linux.  
# Operating systems supported
LinuxSC supports most major distributions of Linux, MacOS, and even Windows.  
It also supports all versions of Discord (PTB, Stable, Canary, etc.)  

# MacOS Support
If you wish to use this on MacOS you'll first need to download Python 3 via [Brew](https://brew.sh).  
After installing Brew, enter `brew install python3` in a terminal, then follow the installation guide below.
# Features
- Custom index.js location
- SmartCord updater (this does update ED)
- LinuxSC updater (this does not update SC, it updates the LinuxSC script)
- Automates all SmartCord installation on Linux, MacOS, and Windows.
# Requirements
You will need Python's distutils, which most commonly has the package name `python3-distutils`  
To install Python's distutils on Debian or any Debian derivatives (Ubuntu, Linux Mint) do `sudo apt install python3-distutils`

# Installation and Usage
1. Git clone this repo: `git clone https://github.com/smartfrigde/LinuxSC/` in a terminal.
2. cd into the newly cloned repo: `cd LinuxSC`
3. Execute the Python script: `python3 LinuxSC.py` and follow the instructions.
4. Restart Discord entirely.
That's it! SmartCord is now installed.
