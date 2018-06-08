import csv
import pycanvass.global_variables as gv
import subprocess
import json
import pycanvass.blocks as blocks
import pycanvass.resiliency as res
import pycanvass.utilities as util
import pycanvass.data_visualization as dv
import random
import numpy as np
import os
import re

def import_from_gridlabd(file_or_folder_name):
    """
    This function creates summary of large GridLAB-D files, and optionally helps to create <feeder-name>-node-file.csv and <feeder-name>-edge-file.csv.
    """

    if os.path.isfile(file_or_folder_name):
        temp = os.path.basename(file_or_folder_name)
        filename = os.path.splitext(temp)[0]
        file_extension = os.path.splitext(temp)[1]

        if file_extension == ".glm":
            print("Modeling Summary 3")
            infile = open(file_or_folder_name, 'r')
            node_output_file_name = filename+"-node-file.csv"
            # edge_output_file_name = filename+"-edge-file.csv"
            node_outfile = open(node_output_file_name, 'w')
            lines = infile.readlines()
            # print(lines)
            lineLengthIncrement = 0
            # Write headers of the CSV file here. 
            node_outfile.write("name, phase, lat, long, voltage, load, gen, kind, critical, type, backup_dg, wind_cc, water_cc, seismic_cc, fire_cc, bias\n")
            
            # These are state variables.  There is no error checking, so we rely on
            # well formatted *.GLM files.
            s = 0

            while s < len(lines):
                # Discard Comments
                if re.search("//", lines[s]) == None:
                    if re.search("object node", lines[s]) != None \
                    or re.search("object triplex_node", lines[s]) != None \
                    or re.search("object meter", lines[s]) != None \
                    or re.search("object load", lines[s]) != None \
                    or re.search("object triplex_meter", lines[s]) != None:
                        lineLengthIncrement = 0
                        node_name = ""
                        kind = ""
                        phases = ""
                        voltage = ""
                        node_type = ""
                        output_string = ""

                        all_node_types = ["res","biz","wlf","shl","law"]

                        if re.search("object load", lines[s]) != None:
                            node_type = random.choice(all_node_types)
                        else:
                            node_type = "utl"

                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            # print("Node line number: {}".format(lineLengthIncrement))
                            # print(lines[s + lineLengthIncrement])
                            if re.search("name", lines[s + lineLengthIncrement]) != None:
                                node_name_string = lines[s + lineLengthIncrement].split()
                                
                                # Graphvis format can't handle '-' characters, so they are converted to '_'
                                node_name = node_name_string[1].rstrip(';').replace('-', '_').replace(':', '_')

                            if re.search("bustype", lines[s + lineLengthIncrement]) != None:
                                bus_type_string = lines[s + lineLengthIncrement].split()
                                if bus_type_string[1].rstrip(';').lower() == "swing":
                                    kind = bus_type_string[1].rstrip(';')
                                    node_type = "sub"
                                else:
                                    kind = "PQ"

                            if re.search("phase", lines[s + lineLengthIncrement]) != None:
                                phase_type_string = lines[s + lineLengthIncrement].split()
                                phases = phase_type_string[1].rstrip(';')
                                phases = phases.strip('\"')

                            if re.search("voltage_A", lines[s + lineLengthIncrement]) != None:
                                voltage_value = lines[s + lineLengthIncrement].split()
                                voltage = voltage_value[1].rstrip(";")
                                

                            if re.search("nominal_voltage", lines[s + lineLengthIncrement]) != None:
                                voltage_value = lines[s + lineLengthIncrement].split()
                                voltage = voltage_value[1].rstrip(";")
                                #lineLengthIncrement = lineLengthIncrement + 1
                        if '}' in lines[s + lineLengthIncrement]:
                            output_string = node_name + ", " + phases + ", " + ", " + ", " +voltage + ", " + ", " + kind + ", " + node_type + ", " + ", " + ", " + ", " + ", " + ", " + ", "+"\n"
                            node_outfile.write(output_string)
                            s = s + lineLengthIncrement
                            # lineLengthIncrement = 0
                            # lengthVal = 'None'
                            # break
                
                s = s + 1

            node_outfile.close()
            

        
        else:
            print("[x] {}.{} is not a GridLAB-D File. Not trying to summarize.".format(filename, file_extension))
            return
            
    
    elif os.path.isdir(file_or_folder_name):
        print("[i] Trying to summarize all GridLAB-D Models in: {}".format(file_or_folder_name))
        for f in os.listdir(file_or_folder_name):
            filename = os.path.join(file_or_folder_name, f)
            print("[i] Summarizing: {}".format(filename))
            dv.layout_model(filename)
        
        
    
    else:
        print("[i] The parameter {} you used inside `layout_model({})` was not found to be either file or a directory.".format(file_or_folder_name, file_or_folder_name))
        print("[i] Please re-check the parameter. If error persists, check the Known Issues document.")
        return

    # print("[i] Layout of all GridLAB-D files are complete.")
    # print("[i] SVG files can be viewed in any web browser, and edited using Inkscape.")
    
    return


def write_gld_headers(filename):
    gldfile = open(filename, "w")
    gldfile.write("// Project Name: {}\n"
                  "// Author: {}\n"
                  "// Auto-generated GridLAB-D File by Canvass\n"
                  "// (c) Canvass Copyright: Sayonsom Chanda.\n"
                  "//---------------------------\n\n"
                  "clock{{\n"
                  "\tstarttime '2017-07-10 0:00:00';\n"
                  "\tstoptime '2017-07-11 0:00:00';\n"
                  "}}\n"
                  "module powerflow{{\n"
                  "\tsolver_method NR;\n"
                  "}}\n\n"
                  "module tape;\n\n".format(gv.project["project_name"], gv.project["author"]))
    gldfile.close()


def _distance_between_two_nodes(n1,n2):
    """

    :param n1: Node object
    :param n2: Node object
    :return:
    """
    p1 = [float(n1.lat),float(n1.long)]
    p2 = [float(n2.lat),float(n2.long)]
    distance_in_ft = np.floor(res.distant_between_two_points(p1,p2)*3280.84)
    return distance_in_ft


def write_default_configurations_to_glm(filename):

    # write default line spacing configuration
    # write default underground line configuration
    # write default transformer configuration
    gldfile = open(filename, "a")
    # write default oh line conductor configuration
    gldfile.write("\n\nobject line_configuration {\n"
                  "\tname default_oh_line_config;\n"
                  "\tz11 0.45+1.07j;\n"
                  "\tz12 0.15+0.50j;\n"
                  "\tz13 0.15+0.38j;\n"
                  "\tz21 0.15+0.50j;\n"
                  "\tz22 0.46+1.04j;\n"
                  "\tz23 0.15+0.42j;\n"
                  "\tz31 0.15+0.38j;\n"
                  "\tz32 0.15+0.42j;\n"
                  "\tz33 0.46+1.06j;\n"
                  "}\n\n")
    gldfile.close()


def write_edges_to_glm(filename):
    e_file = gv.filepaths["edges"]
    gldfile = open(filename, "a")
    with open(e_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        edges = csv.reader(f)
        if has_header:
            next(edges)  # Skip header row

        for edge in edges:
            if edge[1].lstrip() == "OH_Line":
                edge_name = edge[0]
                node1 = res.node_object_from_node_name(edge[2].lstrip())
                node2 = res.node_object_from_node_name(edge[3].lstrip())
                dist_between_nodes = _distance_between_two_nodes(node1,node2)
                gldfile.write("\nobject overhead_line {{\n"
                              "\tname {};\n"
                              "\tphases ABCN;\n"
                              "\tfrom {};\n"
                              "\tto {};\n"
                              "\tlength {};\n"
                              "\tconfiguration default_oh_line_config;\n"
                              "}}\n".format(edge_name, edge[2].lstrip(), edge[3].lstrip(), dist_between_nodes))

    gldfile.close()


def write_recorder_to_glm(filename,n):
    gldfile = open(filename, "a")
    gldfile.write("\nobject recorder{{\n"
                  "\tparent {};\n"
                  "\tproperty voltage_A, voltage_B, voltage_C;\n"
                  "\tinterval 3600;\n"
                  "\tlimit 1000;\n"
                  "\tfile measurements_at_{}.csv;\n"
                  "}}\n".format(n,n))
    gldfile.close()


def write_nodes_to_glm(filename):
    n_file = gv.filepaths["nodes"]
    gldfile = open(filename, "a")
    with open(n_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        nodes = csv.reader(f)
        if has_header:
            next(nodes)  # Skip header row

        for node in nodes:
            node_name = node[0]
            if node[7].lstrip() == "SWING":
                gldfile.write("object node {{\n"
                              "\tname {};\n"
                              "\tphases ABCN;\n"
                              "\tnominal_voltage {}.0;\n"
                              "\tbustype SWING;\n"
                              "}}\n".format(node_name, node[4].lstrip()))
            else:
                gldfile.write("object node {{\n"
                              "\tname {};\n"
                              "\tphases ABCN;\n"
                              "\tnominal_voltage {}.0;\n"
                              "}}\n".format(node_name, node[4].lstrip()))



    gldfile.close()


class DistributionSystem:

    def __init__(self, graph):
        self.graph = graph


    def export_to_gridlabd(self):
        print("Convert Graph Model to gridlab-d file")
        filename = str(gv.project["project_name"]) + "_model.glm"
        write_gld_headers(filename)
        write_default_configurations_to_glm(filename)
        write_nodes_to_glm(filename)
        write_edges_to_glm(filename)

    def install_sensor(self,sensor="mpmu",*args):
        filename = str(gv.project["project_name"]) + "_model.glm"
        for a in args:
            if res.node_object_from_node_name(a.lstrip()):
                print("[i] Installing a {} in Node {}.".format(sensor,a.lstrip()))
                write_recorder_to_glm(filename, a.lstrip())
            else:
                print("[x] Cannot install a {} in Node {}.".format(sensor,a.lstrip()))



    def gridlabd_powerflow(self):
        filename = str(gv.project["project_name"]) + "_model.glm"
        try:
            subprocess.check_call(['gridlabd', filename])
        except subprocess.CalledProcessError:
            print("[x] GridLAB-D Model Compilation Failed.")

    def import_from_gridlabd(self):
        print("import from gridlab-d")

    def powerflow(self):
        print("check if graph is valid")
        print("check if gridlabd is installed")
        print("build gridlab-d file")
        print("create a folder for power flow results")
        print("run power flow")

    def reconfigure(self):
        print("run restoration code")
        print()


