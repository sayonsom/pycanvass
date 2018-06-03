import json
from pycanvass.global_variables import *
import re
from pycanvass.blocks import *

def banner(): 
    print("\n" * 100)
    print("|----------------------------------------------|")
    print("| pyCanvass: 0.0.1                             |")
    print("|----------------------------------------------|")
    print("| Resiliency computation tool for Smart Grids  |")
    print("|                                              |")
    print("| Author: Sayonsom Chanda                      |")
    print("| License: GNU Public License, v2: 2016-18     |")
    print("| Support: sayon@ieee.org                      |")
    print("|----------------------------------------------|")


def validate_config_file():
    print("[i] Please include the configuration file in your Python Code like follows, towards the top of your script:")
    print(">> config_file_name = \"<put-in-the-path-to-your-file-here.>\"")
    print(">> project, nodes, blocks = load_project(config_file_name)")



def build_config_file():
    config_file_name = "auto_project_config.json"
    print("|----------------------------------------------|")
    print("| Building a simulation configuration file     |")
    print("|----------------------------------------------|")
    project_name = input("[1 of 9] Name of your project:     ")
    author_name = input("[2 of 9] Author:                   ")
    location = input("[3 of 9] Location:                 ")
    node_file = input("[4 of 9] Path to your node file:   ")
    edge_file = input("[5 of 9] Path to your edge file:   ")
    threat_file = input("[6 of 9] Path to your threat file: ")
    event_name = input("[7 of 9] Event to be simulated:    ")
    event_intensity = input("[8 of 9] Event intensity:          ")
    results_folder = input("[9 of 9] Results folder (Hit Enter for Default): ")

    try:
        if json.loads(data_string):
            print("[i] Your inputs were converted to a valid JSON file.")
            with open(config_file_name,'w+') as filename:
                m = json.dumps(data_string)
                filename.write(m)
    except:
        print("[1] Please use option 1 for now. Fixing it in the next update.")
        

def setup():
    banner()

    make_config_file = input("[?] Do you have an existing configuration file?:\n"
          "[1] Yes\n"
          "[2] No, make a config file for me\n"
          "[3] Load example distribution system\n[>] (Enter a number) ")
    if make_config_file.lstrip() == "1":
        config_file_path = input("[?] Please enter the full path to your configuration file:\n")
        validate_config_file()
    elif make_config_file.lstrip() == "2":
        build_config_file()
    elif make_config_file.lstrip() == "3":
        print("[!] Couldn't find an example model. Contact sayon@ieee.org")
        sys.exit()

    return 0



setup()


from pycanvass.distributionsystem import *
from pycanvass.resiliency import *
from pycanvass.global_variables import *
from pycanvass.data_bridge import *
from pycanvass.complexnetwork import *
from pycanvass.forecast import *
import sys
import getpass

config_file = ""
