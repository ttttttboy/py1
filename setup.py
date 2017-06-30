import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {'packages': [], 'excludes': []}

setup(name="py1",
      version="1.0",
      description="None.",
      options={'build_exe': build_exe_options},
      executables=[Executable('main.py')])
