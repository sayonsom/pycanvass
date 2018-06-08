import subprocess
"""
All the quick utility functions, frequently called in other libraries
"""

_version = "0.0.2.8"

def _hide_terminal_output():
    """
    Configure subprocess to hide the console window
    """
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE

def _banner(): 
    print("\n" * 100)
    print("|----------------------------------------------|")
    print("| pyCanvass: {}                           |".format(_version))
    print("|----------------------------------------------|")
    print("| Resiliency computation tool for Smart Grids  |")
    print("|                                              |")
    print("| Author: Sayonsom Chanda                      |")
    print("| License: GNU Public License, v2: 2016-18     |")
    print("| Support: sayon@ieee.org                      |")
    print("|----------------------------------------------|")
