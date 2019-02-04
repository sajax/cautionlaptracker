import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_exe_options = {"packages": ["os"], "excludes": []}


base = None
if sys.platform == "win32":
    base = "Console"

setup(name = "Caution Lap Tracker",
      version = "1.0.0",
      description = "Caution Lap Tracker",
      options = {"build_exe": build_exe_options},
      executables = [Executable("main.py", base=base)])
