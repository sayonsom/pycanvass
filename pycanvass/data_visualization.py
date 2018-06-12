import numpy as np
import pandas as pd
import matplotlib as mpl
from pathlib import Path
import json
import pycanvass.global_variables as gv
# from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
import subprocess
import sys
import re
import os
import pycanvass.utilities as util
import random
from pycanvass.all import *

# SET PLOT VISUALIZATION DEFAULTS
# -------------------------------
SMALL_FONT = 8
MEDIUM_FONT = 12
LARGE_FONT = 18

plt.rc('figure', titlesize=LARGE_FONT)

# -------------------------------

def _grid(x,y,z, resX = 100,resY=100):
    xi = np.linspace(min(x), max(x), resX)
    yi = np.linspace(min(y), max(y), resY)
    Z = griddata(x,y,z,xi,yi, interp='linear')
    X, Y = np.meshgrid(xi, yi)
    return X, Y, Z

def view_on_a_map(filename,**kwargs):
    """
    Plots a feeder file on a map
    :param filename:
    :param kwargs:
    :return:
    """
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if key == "location":
                location = value
            elif key == "location_latlong":
                location_latlong = value
            elif key == "radius":
                radius = value
            elif key == "basemap":
                basemap = value


def _next_geo_coordinate(geo_coord, distance):
    """
    Calculates the next geo-coordinate.
    If we know one geo-coordinate and how far the coordinate is supposed to be, we can make a random guess about the next co-ordinate point.
    :param geo_coord: tuple containing [lat, long]
    :param distance: in feet.
    :return: next_geo_coord tuple containing [lat, long]

    Note:
    - 1 deg latitude = 111.32 km, or 69 miles, or 364320 feet
    - 1 ft = 0.0003048 km, or 2.7448e-6 latitude shift

    """
    theta = random.randrange(0, 359)
    # direction = ""
    # if theta >= 0 and theta < 30:
    #     direction = "E"
    # elif theta >= 30 and theta < 60:
    #     direction = "NE"
    # elif theta >= 60 and theta < 120:
    #     direction = "N"
    # elif theta >= 120 and theta < 150:
    #     direction = "NW"
    # elif theta >= 150 and theta < 210:
    #     direction = "W"
    # elif theta >= 210 and theta < 240:
    #     direction = "SW"
    # elif theta >= 240 and theta < 300:
    #     direction = "S"
    # elif theta >= 300 and theta < 330:
    #     direction = "SE"
    # elif theta >= 330 and theta < 360:
    #     direction = "E"

    # print("theta {} : direction {}".format(theta, direction))
    if distance != "None":
        next_lat = geo_coord[0] + float(distance)*np.cos(theta * np.pi / 180)*2.7448e-6
        next_long = geo_coord[1] + float(distance)*np.sin(theta * np.pi / 180)*2.7448e-6
        logging.info("_next_geo_coordinate calculated lat: {} long: {}".format(next_lat, next_long))
        return [next_lat, next_long]


def visualize(model_name, mode="contour_plot", criteria="Risk", default_title=True):
    """

    :param mode: (Default: mode="contour_plot") Other options are "bar_plot", "line_chart")
    :param model_name:
    :param criteria: (Default: risk) Other option is resiliency.
    :return:
    """
    expected_file_name = str(model_name) + "-node-latlong-file.csv"
    expected_file_name = Path(expected_file_name)

    if expected_file_name.exists():
        util._hide_terminal_output()
        fields = ['lat', 'long', 'risk']
        print("[i] Plotting contour plot of the {} of {}".format(criteria, model_name))
        df = pd.read_csv(expected_file_name, skipinitialspace=True, usecols=fields)
        x = df.lat
        y = df.long
        z = df.risk
        X, Y, Z = _grid(x,y,z)
        plt.contourf(X, Y, Z)
        if default_title is True:
            project_config_file = open(gv.filepaths["model"])
            project_settings = json.load(project_config_file)
            project_config_file.close()
            plt.title("{} of {} with respect to {} of intensity {}".format(criteria, model_name, project_settings["event"]["type"], project_settings["event"]["known_intensity"]))

        plt.colorbar()
        plt.xlabel("Latitude")
        plt.ylabel("Longitude")
        plt.show()


    else:
        print("[x] Could not find the default risk and resiliency file name for {}".format(model_name))
        print("[i] Please read the documentation on naming conventions")
        logging.error("Couldn't find the default risk and resiliency file name for {}.".format(model_name))



def layout_model(file_or_folder_name, map_random=False):
    """
    Create a tree like layout for a feeder model.
    This is a memory intensive operation, with O(n^3) running time. <-- todo
    Please be patient if you use this operation.

    Caveat: This function does not check if the GridLAB-D model converges or not, so the user is responsible for
    checking model accuracy.

    :param map_random:
    :return:
    :param file_or_folder_name: [1] a GridLAB model file (i.e. file with *.glm extension)
    or, [2] a folder containing multiple GridLAB-D model.

    :return: SVG file (or files) containing the layout of the GridLAB-D Model
    """
    try:
        util._hide_terminal_output()

        if not os.path.exists('C:\\Program Files (x86)\\Graphviz2.38\\bin'):
            print("[x] Dependency Error: Graphviz is not installed.")
            logging.error("Dependency Error: Graphviz is not installed.")
            print("[i] Layout of the GridLAB-D Models will not proceed.")
            print("[i] Please refer to documentation on how to get Graphviz, and set path correctly")
            return
    except Exception:
        
        print("[i] Please refer to documentation")
        logging.error("Error in layout_model -- Tried to search if GraphViz is installed, and failed.")
        return 

    if os.path.isfile(file_or_folder_name):
        temp = os.path.basename(file_or_folder_name)
        filename = os.path.splitext(temp)[0]
        file_extension = os.path.splitext(temp)[1]

        if file_extension == ".glm":

            infile = open(file_or_folder_name, 'r')
            outfile = open(filename, 'w')


            lines = infile.readlines()

            # .dot files begin with the 'graph' or 'digraph' keyword.
            outfile.write("digraph {\n")
            outfile.write("node [shape=box]\n")
            # These are state variables.  There is no error checking, so we rely on
            # well formatted *.GLM files.
            s = 0
            state = 'start'
            edge_color = 'black'
            edge_style = 'solid'
            lengthVal = 0.0
            lineLengthIncrement = 0

            written_nodes = []
            last_node_traversed = []
            if map_random is True:
                node_latlong_file_name = filename + "-node-latlong-file.csv"
                node_latlong_outfile = open(node_latlong_file_name, 'w+')
                node_latlong_outfile.write("node,lat,long,risk\n")

            # Loop through each line in the input file...
            while s < len(lines):
                # Discard Comments
                if re.match("//", lines[s]) == None:
                    if re.search("from", lines[s]) != None:
                        ts = lines[s].split()
                        # Graphviz format can't handle '-' characters, so they are converted to '_'
                        ns = ts[1].rstrip(';').replace('-', '_').replace(':', '_')
                        outfile.write(ns)

                        if len(written_nodes) == 0:
                            print("\n\n[i] Provide substation latitude and longitude (N,E --> +ve, W,S --> -ve)\n... Rest of the network geo-coordinates are randomly populated.")
                            starting_lat = input("[?] Latitude   : ")
                            starting_long = input("[?] Longitude  : ")
                            written_nodes.append(ns)
                            node_latlong_outfile.write(ns + "," + str(starting_lat) + "," + str(starting_long) + "\n")
                            last_node_traversed = [ns, float(starting_lat), float(starting_long)]
                            logging.info("Starting to calculate distance from Lat: {} Long: {}".format(float(starting_lat), float(starting_long)))



                        state = 'after_from'
                    elif state == 'after_from' and re.search("to ", lines[s]) != None:
                        ts = lines[s].split()
                        ns = ts[1].rstrip(';').replace('-', '_').replace(':', '_')
                        if edge_color == 'red':
                            outfile.write(
                                ' -> ' + ns + '[style=' + edge_style + ' color=' + edge_color + ' label="' + lengthVal + '"]\n')
                            outfile.write("node [shape=box]\n")
                            logging.info(
                                "if_loop: Calculating distance from {} to {}, which is Lat: {} Long: {}".
                                    format(last_node_traversed[0], ns, last_node_traversed[1],last_node_traversed[2]))
                            x = _next_geo_coordinate([last_node_traversed[1], last_node_traversed[2]],
                                                     float(lengthVal2))
                            if ns not in written_nodes:
                                node_latlong_outfile.write(ns + "," + str(x[0]) + "," + str(x[1]) + "\n")
                                written_nodes.append(ns)
                            last_node_traversed[0] = ns
                            last_node_traversed[1] = float(x[0])
                            last_node_traversed[2] = float(x[1])

                        else:
                            outfile.write(
                                ' -> ' + ns + '[style=' + edge_style + ' color=' + edge_color + ' label="' + lengthVal2 + '"]\n')
                            logging.info(
                                "else_loop: Calculating distance from {} to {}, which is Lat: {} Long: {}".
                                    format(last_node_traversed[0], ns, last_node_traversed[1], last_node_traversed[2]))
                            x = _next_geo_coordinate([last_node_traversed[1], last_node_traversed[2]],
                                                     float(lengthVal2))
                            if ns not in written_nodes:
                                node_latlong_outfile.write(ns + "," + str(x[0]) + "," + str(x[1]) + "\n")
                                written_nodes.append(ns)

                            last_node_traversed[0] = ns
                            last_node_traversed[1] = float(x[0])
                            last_node_traversed[2] = float(x[1])

                        lengthVal = 0.0
                        # After an edge is added to the graph, reset the states back to default
                        state = 'start'
                        edge_color = 'black'
                        edge_style = 'solid'
                    elif (re.search("object underground_line", lines[s]) is not None) or (
                        re.search("object overhead_line", lines[s]) is not None):
                        while '}' not in lines[s + lineLengthIncrement]:
                            if re.search("length ", lines[s + lineLengthIncrement]) is not None:
                                les = lines[s + lineLengthIncrement].split()
                                if len(les) > 2:
                                    tsVal = les[1] + ' ' + les[2].strip(';')
                                    lengthVal = tsVal
                                elif len(les) <= 2:
                                    tsVal = les[1].strip(';')
                                    lengthVal = tsVal
                                break
                            else:
                                lineLengthIncrement = lineLengthIncrement + 1
                            if '}' in lines[s + lineLengthIncrement]:
                                lineLengthIncrement = 0
                                lengthVal = 0.0
                                break
                        if re.search("object underground_line", lines[s]) is not None:
                            lengthVal2 = lengthVal
                            lengthVal = "UG_line\\n" + str(lengthVal)

                        elif re.search("object overhead_line", lines[s]) is not None:
                            lengthVal2 = lengthVal
                            lengthVal = "OH_line\\n" + str(lengthVal)
                    elif re.search("object transformer", lines[s]) is not None:
                        edge_color = 'red'
                        lengthVal2 = "0.0"
                        lengthVal = "transformer\\n" + str(lengthVal)
                        outfile.write("node [shape=oval]\n")
                    elif re.search("object triplex_line", lines[s]) is not None:
                        edge_color = 'green'
                        lengthVal2 = lengthVal
                        lengthVal = "triplex_line\\n" + str(lengthVal)
                    elif re.search("object fuse", lines[s]) != None:
                        edge_color = 'blue'
                        lengthVal2 = lengthVal
                        lengthVal = "Fuse\\n" + str(lengthVal)
                    elif re.search("phases ", lines[s]) != None:
                        ts = lines[s].split()
                        if len(ts[1].rstrip(';')) > 3:
                            edge_style = 'bold'
                        elif len(ts[1].rstrip(';')) > 2:
                            edge_style = 'dashed'

                s += 1

            outfile.write("}\n")
            infile.close()
            outfile.close()
            os.system("dot -Tsvg -O " + filename)
        
        else:
            print("[x] {}.{} is not a GridLAB-D File. Not trying to layout.".format(filename, file_extension))
            logging.debug("{}.{} is not a GridLAB-D File. Not trying to layout.".format(filename, file_extension))
            
    
    elif os.path.isdir(file_or_folder_name):
        print("[i] Creating a tree layout for all GLM files in: {}".format(file_or_folder_name))
        logging.info("Creating a tree layout all GLM files in: {}".format(file_or_folder_name))
        for f in os.listdir(file_or_folder_name):
            filename = os.path.join(file_or_folder_name, f)
            print("[i] Processing: {}".format(filename))
            logging.debug("Processing: {}".format(filename))
            layout_model(filename)
        
        
    
    else:
        print("[i] The parameter {} you used inside `layout_model({})` was not found to be either file or a directory.".format(file_or_folder_name, file_or_folder_name))
        print("[i] Please re-check the parameter. If error persists, check the Known Issues document.")
        logging.error("The parameter {} you used inside `layout_model({})` was not found to be either file or a directory.".format(file_or_folder_name, file_or_folder_name))
        return

    print("[i] Layout of all GridLAB-D files are complete.")
    logging.info("Layout of all GridLAB-D files are complete.")
    print("[i] SVG files can be viewed in any web browser, and edited using Inkscape.")
    
    return

def realtime_demo():
    """
    """
    plt.axis([0,10,0,1])

    for i in range(10):
        y = np.random.random()
        plt.scatter(i,y)
        plt.pause(0.05)

    plt.show()

