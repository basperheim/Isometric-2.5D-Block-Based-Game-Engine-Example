import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "isoterrain",
        version = "0.1",
        description = "An example of a Minecraft-style 2.5D Isometric game written in Python using Pygame.",
        options = {"build_exe": build_exe_options},
        executables = [Executable("isoterrain.py", base=base)])
