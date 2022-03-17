import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
                    "packages": ["os","PySide6"],
                    "excludes": ["tkinter"],
                    "optimize": True,
                    "include_files":['icons/'],
                    }

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "ECN Manager",
        version = "1.0",
        description = "ECN Manager",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Manager.py",base = base,icon="icons/manager.ico"),Executable("Launcher.py",base = base,icon="icons/launcher.ico"),Executable("Notifier.py",base = base,icon="icons/notifier.ico")])