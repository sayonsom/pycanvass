import json
import os
from pathlib import Path
from pycanvass.global_variables import *
import re
from pycanvass.blocks import *
from pycanvass.utilities import _banner 


def _input_project_config_file():
    current_folder_path, current_folder_name = os.path.split(os.getcwd())
    default_json_file_name = current_folder_path + "\\project_config.json"
    default_json_file_name = Path(default_json_file_name)

    if default_json_file_name.exists():
        print("[i] Loaded default project configuration file: {}".format(default_json_file_name))
        project_config_path = default_json_file_name
        gv.filepaths["model"] = project_config_path
        return True
    else:
        print("[x] Default project configuration file not found.")
        project_config_path= input("\n[i] Please enter the path to the project file (*.JSON):\n")
        gv.filepaths["model"] = project_config_path
        return project_config_path
    
    gv.filepaths["model"] = project_config_path
    

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
    _banner()
    try:
        if _input_project_config_file() is True:
            return 
        else:
            print("[x] Did not find a default project configuration file.\n\n")
            make_config_file = input("[?] Please make one of the following choices:\n"
                "[1] Provide path to project configuration folder\n"
                "[2] No, make a config file for me\n")

            if make_config_file.lstrip() == "1":
                config_file_path = input("[?] Please enter the full path to your configuration file:\n")
                
            elif make_config_file.lstrip() == "2":
                build_config_file()
            else:
                print("[x] Your input was not valid. Please retry.\n\n")
                setup()
    except KeyboardInterrupt:
        y_or_n = input("[x] It seems you wanted to terminate the project. Are you sure? [Y/N]")
        if y_or_n.lstrip() == "Y" or y_or_n.lstrip() == "y" or y_or_n.lstrip() == "Yes" or y_or_n.lstrip() == "yes":
            print("[i] Exiting pyCanvass. Bye.")
            sys.exit()




setup()


from pycanvass.distributionsystem import *
from pycanvass.resiliency import *
from pycanvass.global_variables import *
from pycanvass.data_bridge import *
from pycanvass.complexnetwork import *
from pycanvass.forecast import *
from pycanvass.data_visualization import *
import sys
import getpass

config_file = ""
