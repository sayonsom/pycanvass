import csv
import pycanvass.global_variables as gv
import subprocess
import logging
import json
import pycanvass.blocks as blocks
from pycanvass.all import *
from pycanvass.all import *
import pycanvass.resiliency as res
import pycanvass.utilities as util
import pycanvass.data_visualization as dv
import pycanvass.resiliency as res
from datetime import *
import random
import numpy as np
import os
import re
import fileinput


def clean_windmil_import(filename):
    if os.path.isfile(filename):
        print("[i] Processing and cleansing: {}".format(filename))

    with fileinput.FileInput(filename, inplace=True, backup=".bak") as file:
        for line in file:
            xx = line.replace("{name", "{\n\t\tname")
            xx = xx.replace("; phases", ";\n\t\tphases")
            xx = xx.replace("; nominal_voltage", ";\n\t\tnominal_voltage")
            xx = xx.replace(";  }", ";\n\t}")
            print(xx, end='')

def plot_zip_load(filename):
    pass

def extract_real_power(power_value):
    real_power_value = power_value.split("+",2)[:2]
    real_power_value = ''.join(real_power_value)
    return real_power_value

def import_from_gridlabd(file_or_folder_name, map_random=False, real_power_only=True):
    """
    This function creates summary of large GridLAB-D files, and optionally helps to create
    <feeder-name>-node-file.csv and <feeder-name>-edge-file.csv.
    """

    if os.path.isfile(file_or_folder_name):
        temp = os.path.basename(file_or_folder_name)
        filename = os.path.splitext(temp)[0]
        file_extension = os.path.splitext(temp)[1]

        if file_extension == ".glm":
            print("[i] Importing GridLAB-D Model: {}".format(file_or_folder_name))
            infile = open(file_or_folder_name, 'r')
            node_output_file_name = filename + "-node-file.csv"
            edge_output_file_name = filename + "-edge-file.csv"

            edge_outfile = open(edge_output_file_name, 'w+')
            lines = infile.readlines()
            # print(lines)
            lineLengthIncrement = 0

            # Write headers of the CSV file here.
            edge_outfile.write(
                "name, kind, from_node, to_node, status, equipment, phases, backup, fire_risk, wind_risk, water_risk, rating, hardening, availability, eq_config_file, known_length, repair_cost, repair_time\n")
            # These are state variables.  There is no error checking, so we rely on
            # well formatted *.GLM files.
            s = 0
            # written_nodes = []
            # last_node_traversed = []
            # if map_random is True:
            #     node_latlong_file_name = filename + "-node-latlong-file.csv"
            #     node_latlong_outfile = open(node_latlong_file_name, 'w+')

            while s < len(lines):
                if re.search("//", lines[s]) == None:
                    if re.search("object overhead_line", lines[s]) != None and re.search("conductor", lines[s]) == None:
                        from_node = ""
                        to_node = ""
                        known_length = ""
                        edge_kind = ""
                        equipment = ""
                        edge_name = ""
                        edge_phases = ""
                        equipment = ""
                        status = "1"
                        repair_time = ""
                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            edge_kind = "OH_Line"
                            if re.search("from", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                from_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')


                            elif re.search("to", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                to_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                            elif re.search("length", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                if len(les) > 2:
                                    tsVal = les[1] + ' ' + les[2].strip(';')
                                    known_length = tsVal
                                elif len(les) <= 2:
                                    tsVal = les[1].strip(';')
                                    known_length = tsVal
                            elif re.search("phases", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                edge_phases = les[1].rstrip(';')
                                edge_phases = edge_phases.strip('\"')
                            elif re.search("configuration", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                equipment = les[1].rstrip(';')

                        if '}' in lines[s + lineLengthIncrement]:
                            lineLengthIncrement = 0

                        edge_name = from_node + "_to_" + to_node
                        edge_output_string = edge_name + ", " + edge_kind + ", " + from_node + ", " + to_node + ", " + status + ", " + equipment + ", " + edge_phases + ", , , , , , , , , " + known_length + ", , \n"
                        edge_outfile.write(edge_output_string)

                    elif re.search("object underground_line", lines[s]) is not None and re.search("conductor",
                                                                                                  lines[s]) is None:
                        from_node = ""
                        to_node = ""
                        known_length = ""
                        edge_kind = ""
                        equipment = ""
                        edge_name = ""
                        edge_phases = ""
                        equipment = ""
                        status = "1"
                        repair_time = ""
                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            from_found = False
                            to_found = False
                            edge_kind = "UG_Line"
                            if re.search("from", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                from_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                from_found = True
                            elif re.search("to", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                to_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                to_found = True
                                if from_found and to_found:
                                    edge_name = from_node + "_to_" + to_node
                            elif re.search("length", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                if len(les) > 2:
                                    tsVal = les[1] + ' ' + les[2].strip(';')
                                    known_length = tsVal
                                elif len(les) <= 2:
                                    tsVal = les[1].strip(';')
                                    known_length = tsVal
                            elif re.search("phases", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                edge_phases = les[1].rstrip(';')
                                edge_phases = edge_phases.strip('\"')
                            elif re.search("configuration", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                equipment = les[1].rstrip(';')
                            elif '}' in lines[s + lineLengthIncrement]:
                                lineLengthIncrement = 0
                                known_length = 0
                                break

                        if '}' in lines[s + lineLengthIncrement]:
                            lineLengthIncrement = 0

                        edge_name = from_node + "_to_" + to_node
                        edge_output_string = edge_name + ", " + edge_kind + ", " + from_node + ", " + to_node + ", " + status + ", " + equipment + ", " + edge_phases + ", , , , , , , , , " + str(
                            known_length) + ", , \n"
                        edge_outfile.write(edge_output_string)

                    elif (re.search("object triplex_line", lines[s]) != None):

                        from_node = ""
                        to_node = ""
                        known_length = ""
                        edge_kind = ""
                        equipment = ""
                        edge_name = ""
                        edge_phases = ""
                        equipment = ""
                        status = "1"
                        repair_time = ""
                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            from_found = False
                            to_found = False
                            edge_kind = "dist_Line"
                            if re.search("from", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                from_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                from_found = True
                            elif re.search("to", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                to_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                to_found = True
                                if from_found and to_found:
                                    edge_name = from_node + "_to_" + to_node
                            elif re.search("length", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                if len(les) > 2:
                                    tsVal = les[1] + ' ' + les[2].strip(';')
                                    known_length = tsVal
                                elif len(les) <= 2:
                                    tsVal = les[1].strip(';')
                                    known_length = tsVal
                            elif re.search("phases", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                edge_phases = les[1].rstrip(';')
                                edge_phases = edge_phases.strip('\"')
                            elif re.search("configuration", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                equipment = les[1].rstrip(';')
                            elif '}' in lines[s + lineLengthIncrement]:
                                lineLengthIncrement = 0
                                known_length = 0
                                break
                        if '}' in lines[s + lineLengthIncrement]:
                            lineLengthIncrement = 0

                        edge_name = from_node + "_to_" + to_node
                        edge_output_string = edge_name + ", " + edge_kind + ", " + from_node + ", " + to_node + ", " + str(status) + ", " + equipment + ", " + edge_phases + ", , , , , , , , , " + str(known_length) + ", , \n"
                        edge_outfile.write(edge_output_string)

                    elif (re.search("object transformer", lines[s]) is not None) and re.search("configuration",
                                                                                               lines[s]) is None:
                        from_node = ""
                        to_node = ""
                        known_length = ""
                        edge_kind = ""
                        equipment = ""
                        edge_name = ""
                        edge_phases = ""
                        equipment = ""
                        status = "1"
                        repair_time = ""
                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            from_found = False
                            to_found = False
                            edge_kind = "transformer"
                            if re.search("from", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                from_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                from_found = True
                            elif re.search("to", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                to_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                to_found = True
                                if from_found and to_found:
                                    edge_name = from_node + "_to_" + to_node
                            elif re.search("phases", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                edge_phases = les[1].rstrip(';')
                                edge_phases = edge_phases.strip('\"')
                            elif re.search("configuration", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                equipment = les[1].rstrip(';')
                            elif '}' in lines[s + lineLengthIncrement]:
                                lineLengthIncrement = 0
                                break

                        if '}' in lines[s + lineLengthIncrement]:
                            lineLengthIncrement = 0

                        edge_name = from_node + "_to_" + to_node
                        edge_output_string = edge_name + ", " + edge_kind + ", " + from_node + ", " + to_node + ", " + status + ", " + equipment + ", " + edge_phases + ", , , , , , , , , " + known_length + ", , \n"
                        edge_outfile.write(edge_output_string)

                    elif (re.search("object fuse", lines[s]) != None):
                        from_node = ""
                        to_node = ""
                        known_length = ""
                        edge_kind = ""
                        equipment = ""
                        edge_name = ""
                        edge_phases = ""
                        equipment = ""
                        status = "1"
                        repair_time = ""
                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            from_found = False
                            to_found = False
                            edge_kind = "fuse"
                            if re.search("from", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                from_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                from_found = True
                            elif re.search("to", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                to_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                to_found = True
                                if from_found and to_found:
                                    edge_name = from_node + "_to_" + to_node
                            elif re.search("phases", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                edge_phases = les[1].rstrip(';')
                                edge_phases = edge_phases.strip('\"')
                            elif re.search("phase_A_state", lines[s + lineLengthIncrement]) != None \
                                    or re.search("phase_B_state", lines[s + lineLengthIncrement]) != None \
                                    or re.search("phase_C_state", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                status_str = les[1].rstrip(';')
                                if status_str.lstrip() == "BLOWN":
                                    status = "0"
                            elif re.search("mean_replacement_time", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                repair_time = les[1].rstrip(';')
                            elif '}' in lines[s + lineLengthIncrement]:
                                lineLengthIncrement = 0
                                break
                        if '}' in lines[s + lineLengthIncrement]:
                            lineLengthIncrement = 0

                        edge_name = from_node + "_to_" + to_node
                        edge_output_string = edge_name + ", " + edge_kind + ", " + from_node + ", " + to_node + ", " + status + ", " + equipment + ", " + edge_phases + ", , , , , , , , , " + known_length + ", , \n"
                        edge_outfile.write(edge_output_string)

                    elif (re.search("object switch", lines[s]) != None):
                        from_node = ""
                        to_node = ""
                        known_length = ""
                        edge_kind = ""
                        equipment = ""
                        edge_name = ""
                        edge_phases = ""
                        equipment = ""
                        status = "1"
                        repair_time = ""
                        while '}' not in lines[s + lineLengthIncrement]:
                            lineLengthIncrement += 1
                            from_found = False
                            to_found = False
                            edge_kind = "switch"
                            if re.search("from", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                from_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                from_found = True
                            elif re.search("to", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                to_node = les[1].rstrip(';').replace('-', '_').replace(':', '_')
                                to_found = True
                                if from_found and to_found:
                                    edge_name = from_node + "_to_" + to_node
                            elif re.search("phases", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                edge_phases = les[1].rstrip(';')
                                edge_phases = edge_phases.strip('\"')
                            elif re.search("phase_A_state", lines[s + lineLengthIncrement]) != None \
                                    or re.search("phase_B_state", lines[s + lineLengthIncrement]) != None \
                                    or re.search("phase_C_state", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                status_str = les[1].rstrip(';')
                                if status_str.lstrip().lower() == "open":
                                    status = "0"
                            elif re.search("mean_replacement_time", lines[s + lineLengthIncrement]) != None:
                                les = lines[s + lineLengthIncrement].split()
                                repair_time = les[1].rstrip(';')
                            elif '}' in lines[s + lineLengthIncrement]:
                                lineLengthIncrement = 0
                                break
                        if '}' in lines[s + lineLengthIncrement]:
                            lineLengthIncrement = 0

                        edge_name = from_node + "_to_" + to_node
                        edge_output_string = edge_name + ", " + edge_kind + ", " + from_node + ", " + to_node + ", " \
                                             + status + ", " + equipment + ", " + edge_phases + ", , , , , , , , , " \
                                             + known_length + ", , \n"
                        edge_outfile.write(edge_output_string)
                s = s + 1

            ## BUILD NODE FILE HERE
            s = 0

            edge_outfile.close()

            node_outfile = open(node_output_file_name, 'w')
            node_outfile.write("name, phase, lat, long, voltage, load, gen, kind, critical, type, backup_dg, wind_cc, "
                               "water_cc, seismic_cc, fire_cc,preexisting_damage,availability,foliage,mttr,op_cost,"
                               "repair_cost,load_type,phase_a_z,phase_a_i,phase_a_p,phase_b_z,phase_b_i,phase_b_p,phase_c_z,phase_c_i,phase_c_p\n")

            while s < len(lines):

                # Discard Comments
                if re.search("//", lines[s]) is None:
                    if re.search("object node", lines[s]) is not None \
                            or re.search("object triplex_node", lines[s]) is not None \
                            or re.search("object meter", lines[s]) is not None \
                            or re.search("object load", lines[s]) is not None \
                            or re.search("object triplex_meter", lines[s]) is not None:

                        lineLengthIncrement = 0
                        node_name = ""
                        kind = ""
                        phases = ""
                        voltage = ""
                        node_type = ""
                        load_type = ""
                        phase_a_z = ""
                        phase_a_i = ""
                        phase_a_p = ""
                        phase_b_z = ""
                        phase_b_i = ""
                        phase_b_p = ""
                        phase_c_z = ""
                        phase_c_i = ""
                        phase_c_p = ""

                        output_string = ""

                        all_node_types = ["res", "biz", "wlf", "shl", "law"]

                        if re.search("object load", lines[s]) is not None:
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

                            if re.search("phase", lines[s + lineLengthIncrement]) is not None:
                                phase_type_string = lines[s + lineLengthIncrement].split()
                                phases = phase_type_string[1].rstrip(';')
                                phases = phases.strip('\"')

                            if re.search("voltage_A", lines[s + lineLengthIncrement]) is not None \
                                    and re.search("measured", lines[s + lineLengthIncrement]) is None:
                                voltage_value = lines[s + lineLengthIncrement].split()
                                voltage = voltage_value[1].rstrip(";")

                            if re.search("nominal_voltage", lines[s + lineLengthIncrement]) is not None:
                                voltage_value = lines[s + lineLengthIncrement].split()
                                voltage = voltage_value[1].rstrip(";")

                            if re.search("constant_impedance_A", lines[s + lineLengthIncrement]) is not None:
                                phase_a_z_value = lines[s + lineLengthIncrement].split()
                                phase_a_z = phase_a_z_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_a_z = extract_real_power(phase_a_z)
                                    phase_a_z = phase_a_z.replace("+","")

                            if re.search("constant_impedance_B", lines[s + lineLengthIncrement]) is not None:
                                phase_b_z_value = lines[s + lineLengthIncrement].split()
                                phase_b_z = phase_b_z_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_b_z = extract_real_power(phase_b_z)
                                    phase_b_z = phase_b_z.replace("+", "")

                            if re.search("constant_impedance_C", lines[s + lineLengthIncrement]) is not None:
                                phase_c_z_value = lines[s + lineLengthIncrement].split()
                                phase_c_z = phase_c_z_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_c_z = extract_real_power(phase_c_z)
                                    phase_c_z = phase_c_z.replace("+", "")

                            if re.search("constant_current_A", lines[s + lineLengthIncrement]) is not None:
                                phase_a_i_value = lines[s + lineLengthIncrement].split()
                                phase_a_i = phase_a_i_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_a_i = extract_real_power(phase_a_i)
                                    phase_a_i = phase_a_i.replace("+","")

                            if re.search("constant_current_B", lines[s + lineLengthIncrement]) is not None:
                                phase_b_i_value = lines[s + lineLengthIncrement].split()
                                phase_b_i = phase_b_i_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_b_i = extract_real_power(phase_b_i)
                                    phase_b_i = phase_b_i.replace("+","")

                            if re.search("constant_current_C", lines[s + lineLengthIncrement]) is not None:
                                phase_c_i_value = lines[s + lineLengthIncrement].split()
                                phase_c_i = phase_c_i_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_c_i = extract_real_power(phase_c_i)
                                    phase_c_i = phase_c_i.replace("+","")

                            if re.search("constant_power_A", lines[s + lineLengthIncrement]) is not None:
                                phase_a_p_value = lines[s + lineLengthIncrement].split()
                                phase_a_p = phase_a_p_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_a_p = extract_real_power(phase_a_p)
                                    phase_a_p = phase_a_p.replace("+","")


                            if re.search("constant_power_B", lines[s + lineLengthIncrement]) is not None:
                                phase_b_p_value = lines[s + lineLengthIncrement].split()
                                phase_b_p = phase_b_p_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_b_p = extract_real_power(phase_b_p)
                                    phase_b_p = phase_b_p.replace("+","")


                            if re.search("constant_power_C", lines[s + lineLengthIncrement]) is not None:
                                phase_c_p_value = lines[s + lineLengthIncrement].split()
                                phase_c_p = phase_c_p_value[1].rstrip(";")
                                if real_power_only is True:
                                    phase_c_p = extract_real_power(phase_c_p)
                                    phase_c_p = phase_c_p.replace("+","")


                        output_string = node_name + ", " + phases + ",,, " + voltage + ",,," + \
                                        kind + ",," + node_type + ",,,,,,,,,,,,," + phase_a_z + ", " + \
                                        phase_a_i + ", " + phase_a_p + ", " + phase_b_z + ", " + phase_b_i + ", " + \
                                        phase_b_p + ", " + phase_c_z + ", " + phase_c_i + ", " + phase_c_p + "\n"



                        if '}' in lines[s + lineLengthIncrement]:
                            #                 + "\n"
                            node_outfile.write(output_string)
                            s = s + lineLengthIncrement
                            # lineLengthIncrement = 0
                            # lengthVal = 'None'
                            # break

                s = s + 1

            node_outfile.close()



        else:
            print("[x] {}.{} is not a GridLAB-D File. Importing is canceled.".format(filename, file_extension))
            return


    elif os.path.isdir(file_or_folder_name):
        print("[i] Importing to GridLAB-D Models in: {}".format(file_or_folder_name))
        for f in os.listdir(file_or_folder_name):
            filename = os.path.join(file_or_folder_name, f)
            print("[i] Processing: {}".format(filename))
            dv.layout_model(filename)



    else:
        print(
            "[i] The parameter {} you used inside `layout_model({})` was not found to be either file or a directory.".format(
                file_or_folder_name, file_or_folder_name))
        print("[i] Please re-check the parameter. If error persists, check the Known Issues document.")
        return

    print("[i] Import of all GridLAB-D files are complete.")
    logging.info("Import of all GridLAB-D files are complete.")
    # print("[i] SVG files can be viewed in any web browser, and edited using Inkscape.")

    return


def write_gld_headers(filename, start_time):
    gldfile = open(filename, "w")
    if start_time is not None:
        start_time_value = start_time
    else:
        start_time_value = '2017-07-10 00:00:00 PDT'
    gldfile.write("// Project Name: {}\n"
                  "// Author: {}\n"
                  "// Auto-generated GridLAB-D File by Canvass\n"
                  "// (c) Canvass Copyright: Sayonsom Chanda.\n"
                  "//---------------------------\n\n"
                  "clock{{\n"
                  "\tstarttime '{}';\n"
                  "}}\n"
                  "module powerflow{{\n"
                  "\tsolver_method FBS;\n"
                  "}}\n\n"
                  "module tape;\n\n".format(gv.project["project_name"], gv.project["author"], start_time_value))
    gldfile.close()


def _distance_between_two_nodes(n1, n2):
    """

    :param n1: Node object
    :param n2: Node object
    :return:
    """
    p1 = [float(n1.lat), float(n1.long)]
    p2 = [float(n2.lat), float(n2.long)]
    distance_in_ft = np.floor(res.distant_between_two_points(p1, p2) * 3280.84)
    return distance_in_ft


def write_power_system_state_recorder(filename):
    gldfile = open(filename, "a")
    gldfile.write("\n\nobject voltdump {\n"
                  "\tfilename voltage_op.csv;\n"
                  "\tmode polar;\n};\n"
                  "\nobject currdump {\n"
                  "\tfilename current_op.csv;\n"
                  "\tmode polar;\n"
                  "};\n\n")
    gldfile.close()


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
                  "}\n\n"
                  "\n\nobject transformer_configuration {\n"
                  "\tname default_xmfr_config;\n"
                  "\tconnect_type DELTA_GWYE;\n"
                  "\tpower_rating 500;\n"
                  "\tprimary_voltage 4160;\n"
                  "\tsecondary_voltage 480;\n"
                  "\tresistance 0.01;\n"
                  "\treactance 0.08;\n"
                  "}\n\n"
                  "\n\nobject regulator_configuration {\n"
                  "\tname default_regulator_config;\n"
                  "\tconnect_type WYE_WYE;\n"
                  "\tband_width 2;\n"
                  "\tband_center 122;\n"
                  "\tcompensator_r_setting_A 3;\n"
                  "\tcompensator_r_setting_B 3;\n"
                  "\tcompensator_r_setting_C 3;\n"
                  "\tcompensator_x_setting_A 9;\n"
                  "\tcompensator_x_setting_B 9;\n"
                  "\tcompensator_x_setting_C 9;\n"
                  "\tpower_transducer_ratio 40;\n"
                  "\traise_taps 16;\n"
                  "\tlower_taps 16;\n"
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

            if edge[1].lstrip() == "regulator":
                edge_name = edge[0]
                from_node = edge[2].lstrip()
                node_obj = res.node_object_from_node_name(from_node)
                gldfile.write("\nobject regulator {{\n"
                              "\tname {};\n"
                              "\tphases {};\n"
                              "\tfrom {};\n"
                              "\tto {};\n"
                              "\tconfiguration default_regulator_config;\n"
                              "}}\n".format(edge_name, node_obj.phase, edge[2].lstrip(), edge[3].lstrip()))

            if edge[1].lstrip() == "transformer":
                edge_name = edge[0]
                from_node = edge[2].lstrip()
                node_obj = res.node_object_from_node_name(from_node)
                gldfile.write("\nobject transformer {{\n"
                              "\tname {};\n"
                              "\tphases {};\n"
                              "\tfrom {};\n"
                              "\tto {};\n"
                              "\tconfiguration default_xmfr_config;\n"
                              "}}\n".format(edge_name, node_obj.phase, edge[2].lstrip(), edge[3].lstrip()))

            if edge[1].lstrip() == "switch":
                edge_name = edge[0]
                from_node = edge[2].lstrip()
                node_obj = res.node_object_from_node_name(from_node)
                status_string = "CLOSED"
                if edge[4].lstrip() == "0":
                    status_string = "OPEN"
                gldfile.write("\nobject switch {{\n"
                              "\tname {};\n"
                              "\tphases {};\n"
                              "\tfrom {};\n"
                              "\tto {};\n"
                              "\tstatus {};\n"
                              "}}\n".format(edge_name, node_obj.phase, edge[2].lstrip(), edge[3].lstrip(),
                                            status_string))

            if edge[1].lstrip() == "OH_Line":
                edge_name = edge[0]
                node1 = res.node_object_from_node_name(edge[2].lstrip())
                node2 = res.node_object_from_node_name(edge[3].lstrip())
                dist_between_nodes = _distance_between_two_nodes(node1, node2)
                gldfile.write("\nobject overhead_line {{\n"
                              "\tname {};\n"
                              "\tphases {};\n"
                              "\tfrom {};\n"
                              "\tto {};\n"
                              "\tlength {};\n"
                              "\tconfiguration default_oh_line_config;\n"
                              "}}\n".format(edge_name, node1.phase, edge[2].lstrip(), edge[3].lstrip(),
                                            dist_between_nodes))

    gldfile.close()


def write_recorder_to_glm(filename, n):
    gldfile = open(filename, "a")
    gldfile.write("\nobject recorder{{\n"
                  "\tparent {};\n"
                  "\tproperty voltage_A, voltage_B, voltage_C;\n"
                  "\tinterval 3600;\n"
                  "\tlimit 1000;\n"
                  "\tfile measurements_at_{}.csv;\n"
                  "}}\n".format(n, n))
    gldfile.close()


def write_nodes_to_glm(filename):
    n_file = gv.filepaths["edges"]
    gldfile = open(filename, "a")
    written_nodes = []
    with open(n_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        nodes = csv.reader(f)
        if has_header:
            next(nodes)  # Skip header row

        written_nodes = []

        for node in nodes:
            from_node = node[2].lstrip()
            to_node = node[3].lstrip()

            if from_node not in written_nodes:
                node_obj = res.node_object_from_node_name(from_node)
                if node_obj.kind.lstrip() == "SWING":
                    gldfile.write("object node {{\n"
                                  "\tname {};\n"
                                  "\tphases {};\n"
                                  "\tnominal_voltage {}.0;\n"
                                  "\tbustype SWING;\n"
                                  "}};\n\n".format(from_node, node_obj.phase, node_obj.voltage))
                elif node_obj.kind.lstrip() == "PQ":
                    load_value_kva = float(node_obj.load.lstrip()) / 3.0
                    gldfile.write("object load {{\n"
                                  "\tname {};\n"
                                  "\tphases {};\n"
                                  "\tnominal_voltage {}.0;\n"
                                  "\tconstant_power_A {};\n"
                                  "\tconstant_power_B {};\n"
                                  "\tconstant_power_C {};\n"
                                  "}};\n".format(from_node, node_obj.phase, node_obj.voltage, load_value_kva,
                                                 load_value_kva, load_value_kva))
                else:
                    gldfile.write("object node {{\n"
                                  "\tname {};\n"
                                  "\tphases {};\n"
                                  "\tnominal_voltage {}.0;\n"
                                  "}};\n\n".format(from_node, node_obj.phase, node_obj.voltage))
                written_nodes.append(from_node)

            if to_node not in written_nodes:
                node_obj = res.node_object_from_node_name(to_node)
                if node_obj.kind.lstrip() == "SWING":
                    gldfile.write("object node {{\n"
                                  "\tname {};\n"
                                  "\tphases {};\n"
                                  "\tnominal_voltage {}.0;\n"
                                  "\tbustype SWING;\n"
                                  "}};\n\n".format(to_node, node_obj.phase, node_obj.voltage))
                elif node_obj.kind.lstrip() == "PQ":
                    load_value_kva = float(node_obj.load.lstrip()) / 3.0
                    gldfile.write("object load {{\n"
                                  "\tname {};\n"
                                  "\tphases {};\n"
                                  "\tnominal_voltage {}.0;\n"
                                  "\tconstant_power_A {};\n"
                                  "\tconstant_power_B {};\n"
                                  "\tconstant_power_C {};\n"
                                  "}};\n\n".format(to_node, node_obj.phase, node_obj.voltage, load_value_kva,
                                                   load_value_kva, load_value_kva))
                else:
                    gldfile.write("object node {{\n"
                                  "\tname {};\n"
                                  "\tphases {};\n"
                                  "\tnominal_voltage {}.0;\n"
                                  "}};\n\n".format(to_node, node_obj.phase, node_obj.voltage))

                written_nodes.append(to_node)

    gldfile.close()


def find_pc(array, matrix=False):
    if matrix:
        first_node=0
        last_node=len (array) - 1
        probabilities=np.unique (array.ravel ())
        low=0
        high=len (probabilities)

        while high - low > 1:
            i=(high + low) // 2
            prob=probabilities[i]
            copied_array=np.array (array)
            copied_array[copied_array < prob]=0.0
            graph=nx.from_numpy_matrix (copied_array)
            if nx.has_path (graph, first_node, last_node):
                low=i
            else:
                high=i

        return probabilities[low]
    else:
        print("[x] Not in this version. Please update.")
        return 0

class DistributionSystem:

    def __init__(self, graph):
        self.graph = graph

    def export_to_gridlabd(self, start_time=None):
        print("Convert Graph Model to gridlab-d file")
        filename = "gridlabd_model.glm"
        gv.user_timezone = gv.project["timezone"]
        if start_time is not None:
            datetime_obj = datetime.strptime(start_time, "%Y/%m/%d %H:%M:%S")
            month_value = "{:02d}".format(datetime_obj.month)
            hour_value = "{:02d}".format(datetime_obj.hour)
            day_value = "{:02d}".format(datetime_obj.day)
            minute_value = "{:02d}".format(datetime_obj.minute)
            second_value = "{:02d}".format(datetime_obj.second)
            start_time_value = str(
                datetime_obj.year) + "-" + month_value + "-" + day_value + " " + hour_value + ":" + minute_value + ":" + second_value + " " + gv.user_timezone
        else:
            start_time_value = None

        write_gld_headers(filename, start_time_value)
        write_default_configurations_to_glm(filename)
        write_nodes_to_glm(filename)
        write_edges_to_glm(filename)
        write_power_system_state_recorder(filename)

    def install_sensor(self, sensor="mpmu", *args):
        filename = str(gv.project["project_name"]) + "_model.glm"
        for a in args:
            if res.node_object_from_node_name(a.lstrip()):
                print("[i] Installing a {} in Node {}.".format(sensor, a.lstrip()))
                write_recorder_to_glm(filename, a.lstrip())
            else:
                print("[x] Cannot install a {} in Node {}.".format(sensor, a.lstrip()))

    def gridlabd_powerflow(self, mode=None):
        if mode is None:
            filename = str(gv.project["project_name"]) + "_model.glm"
        elif mode.lstrip() == "timeseries":
            filename = "gridlabd_model.glm"
        else:
            filename = "gridlabd_model.glm"
        try:
            subprocess.check_call(['gridlabd', filename])
        except subprocess.CalledProcessError:
            print("[x] GridLAB-D Simulation was not completed.")

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
