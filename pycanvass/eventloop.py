import pycanvass.data_bridge as db
import pycanvass.global_variables as gv
import pycanvass.resiliency as resy
import pycanvass.blocks as blocks
import pycanvass.complexnetwork as cn
import pycanvass.distributionsystem as ds
import re
import csv
import pandas as pd
import logging
# import pycanvass.complexnetworks as cn
import os
from datetime import *
import json

from shutil import copy



def create_timestamped_node_file(node_to_modify, **kwargs):
    """
    d
    :param timestamp:
    :param node_to_modify:
    :param args:
    :return:
    """
    new_rows = []
    if os.path.isfile('node-file.csv'):
        n_file='node-file.csv'
    else:
        n_file = gv.filepaths["nodes"]

    node_search_result = db._node_search(node_to_modify)
    if node_search_result == 0:
        return

    for k, v in kwargs.items():
        if k == "new_load":
            new_load_value = v
        if k == "new_gen":
            new_gen_value = v
    load_key = "new_load"
    gen_key = "new_gen"
    criticality_key = "new_status"
    with open(n_file, 'r+') as f:
        csvr = csv.reader(f)
        csvr = list(csvr)
        for row in csvr:
            new_row = row
            if row[0].lstrip() == node_to_modify.lstrip() or row[9].lstrip() == node_to_modify.lstrip():

                if load_key in kwargs:
                    new_row[5] = kwargs[load_key]

                if gen_key in kwargs:
                    new_row[6] = kwargs[gen_key]

            new_rows.append(new_row)

    new_node_filename = 'node-file.csv'

    with open(new_node_filename, 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)
    full_new_file_path = os.path.join(os.getcwd(), new_node_filename)
    print(full_new_file_path)
    gv.filepaths["nodes"] = full_new_file_path


def create_timestamped_edge_file(timestamp, edge_to_modify, **kwargs):
    """
    d
    :param timestamp:
    :param edge_to_modify:
    :param args:
    :return:
    """
    new_rows = []
    n_file = gv.filepaths["nodes"]

    node_search_result = _node_search(edge_to_modify)
    if node_search_result == 0:
        return

    for k, v in kwargs.items():
        if k == "new_load":
            new_load_value = v
        if k == "new_gen":
            new_gen_value = v
    load_key = "new_load"
    gen_key = "new_gen"
    status_key = "new_status"
    with open(n_file, 'r+') as f:
        csvr = csv.reader(f)
        csvr = list(csvr)
        for row in csvr:
            new_row = row
            if row[0].lstrip() == edge_to_modify.lstrip() or row[9].lstrip() == edge_to_modify.lstrip():

                if load_key in kwargs:
                    new_row[5] = kwargs[load_key]

                if gen_key in kwargs:
                    new_row[6] = kwargs[gen_key]

            new_rows.append(new_row)

    new_node_filename = timestamp + "-temp-node-file.csv"
    logging.info("Creating a temporary load file called {}".format(new_node_filename))


    with open(new_node_filename, 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    gv.filepaths["nodes"] = new_node_filename


def search_string_in_df(df, val):
    try:
        a = df.index[df['timestamp'].str.contains(val)]
    except:
        a = df.index[df['anchor_name'].str.contains(val)]
    logging.info("Searching for {} in dataframe".format(val))
    if a.empty:
        print("[x] No corresponding time series data was found")
        logging.error("Failed at line 115 of eventloop. No corresponding time series data was found")
        raise ValueError
    elif len(a) > 1:
        print("[x] Multiple timestamps found")
        logging.error("Failed at line 119 of eventloop. Multiple corresponding time series data were found")
        raise ValueError
    else:
        # most usual case, only one-time stamp will be found.
        return a.item()


def create_threatfile(threatfile, timestamp):
    df = pd.read_csv(threatfile, skipinitialspace=True)
    fields = list(df)
    threat_anchor_names = []
    df = pd.read_csv(threatfile, skipinitialspace=True, usecols=fields)
    logging.info("Writing threatfile for timestamp = {}".format(timestamp))
    row_number = search_string_in_df(df, timestamp)
    logging.info("Getting data from row number {}".format(row_number))
    with open("threat-file.csv", "w+") as file:
        file.write("anchor_name,lat,long,strength,water_level,wind_speed,fire_temp,seismic_activity,confidence_factor\n")
        for f in fields:
            if "-wind" in f:
                threat_name = re.split("-wind", f, maxsplit=1)[0]
                wind_risk_index_of_threat = fields.index(f)
                wind_risk_value = df.iloc[row_number, wind_risk_index_of_threat]
                water_risk_value = df.iloc[row_number, wind_risk_index_of_threat+1]
                fire_risk_value = df.iloc[row_number, wind_risk_index_of_threat+2]
                seismic_risk_value = df.iloc[row_number, wind_risk_index_of_threat+3]
                confidence_factor = df.iloc[row_number, wind_risk_index_of_threat+4]
                threat_obj = gv.threat_dict[threat_name]
                write_string = "{},{},{},,{},{},{},{},{}\n".format(threat_obj.anchor, threat_obj.lat, threat_obj.long, water_risk_value, wind_risk_value, fire_risk_value, seismic_risk_value, confidence_factor)
                file.write(write_string)

def reverse_time_step(timestampvalue):
    timestampvalue_array = list(timestampvalue)
    year = timestampvalue_array[0:4]
    year = ''.join(year)
    month = timestampvalue_array[4:6]
    month = ''.join(month)
    day = timestampvalue_array[6:8]
    day = ''.join(day)
    hour = timestampvalue_array[8:10]
    hour = ''.join(hour)
    minute = timestampvalue_array[10:12]
    minute = ''.join(minute)
    if len(timestampvalue_array) > 12:
        second = timestampvalue_array[11:12]
        second = ''.join(second)
        second = ":"+second
    else:
        second = ""
    if len(timestampvalue_array) > 13:
        extra = timestampvalue_array[13:]
    else:
        extra = ""
    reverse_time_step_string = year + "/" + month + "/" + day + " " + hour + ":" + minute + second
    return reverse_time_step_string

def timeseries_simulation(simulation_folder, start_time="", interval_time="", stop_time="", powerflow = False):

    subfolders = [f.name for f in os.scandir(simulation_folder) if f.is_dir()]

    for s in subfolders:
        timestring = reverse_time_step(s)
        print("[i] Performing event simulation for time-step {}".format(timestring))
        # logging.info("Performing event simulation for time-step {}".format(timestring))
        automatic_impact_of_event(simulation_folder, s)
        newpath = os.path.join(simulation_folder, s)
        os.chdir(newpath)
        nodes, edges = blocks.load_project_ts()

        network = cn.build_network_2(nodes, edges, timestring)

        mygraph = network["normal"]

        if powerflow is True:

            try:
                from pycanvass.utilities import _hide_terminal_output
                _hide_terminal_output()
                dist_system = ds.DistributionSystem(mygraph)
                print("[i] Attempting power-flow for {}".format(timestring))
                dist_system.export_to_gridlabd(start_time=timestring)
                dist_system.gridlabd_powerflow(mode="timeseries")
            except Exception as e:
                print("[x] GridLAB-D Model simulation could not be completed for {}\n... Read events log file for details".format(timestring))
                logging.error(" GridLAB-D Model simulation could not be completed for {}\n\tDetails: {}".format(timestring, e))

        else:
            logging.info("skipping power flow for time-step {}".format(timestring))



        resy.nodal_calculations(mygraph)


        print("[i] Nodal Resiliency Computation Complete for {}".format(s))





def modify_edge_file():
    """

    :param timeseries_dict:
    :param vary_gen:
    :param vary_criticality:
    :return:
    """
    # Copy edge file from previous time-step here
    new_edit_file = gv.filepaths["edges"]
    dst = os.path.join(os.getcwd(), 'edge-file.csv')
    from shutil import copy
    copy(new_edit_file, dst)




def automatic_impact_of_event(simulation_folder_path, foldername):
    """
    This function helps create the edge file appropriate for the time stamp, and takes back the control of the program
    to the main directory where all the other time-stamped folders are located.
    :param simulation_folder_path:
    :param foldername:
    :return:
    """

    u_settings = open(gv.filepaths['user_preferences'])
    settings = json.load(u_settings)
    u_settings.close()

    main_working_dir = simulation_folder_path  # gv.main_working_dir
    newpath = os.path.join(main_working_dir, foldername)
    os.chdir(newpath)
    nodefile = os.path.join(newpath, 'node-file.csv')
    threatfile = os.path.join(newpath, 'threat-file.csv')
    edgefile = os.path.join(newpath, 'edge-file.csv')

    gv.filepaths["edges"]

    if os.path.isfile(nodefile):
        if os.path.isfile(threatfile):
            # load edge file from previous stage
            e_file = edgefile
            # from node threat anchor point -- node availability 1 or 0
            fields = ["anchor_name", "water_level", 'wind_speed', "fire_temp", "seismic_activity", "confidence_factor"]
            t_df = pd.read_csv(threatfile, skipinitialspace=True, usecols=fields)
            with open(e_file) as f:
                edges = csv.reader(f)
                next(edges, None)
                for edge in edges:
                    type_of_edge = edge[1].lstrip()
                    from_node = edge[2].lstrip()
                    from_node_obj = resy.node_object_from_node_name(from_node)
                    threat_anchor = resy.primary_threat_anchor_of_node(from_node_obj)
                    threat_row = search_string_in_df(t_df, threat_anchor["name"])
                    wind_risk = t_df['wind_speed'][threat_row]
                    fire_risk = t_df['fire_temp'][threat_row]
                    seismic_risk = t_df['seismic_activity'][threat_row]
                    water_risk = t_df['water_level'][threat_row]
                    if type_of_edge == "OH_Line":
                        logging.info("automatic event upon OH Line")
                        if float(settings["tolerances"]["OH_Line"]["wind"]) < float(wind_risk) or float(settings["tolerances"]["OH_Line"]["water"]) < float(water_risk) or float(settings["tolerances"]["OH_Line"]["fire"]) < float(fire_risk) or float(settings["tolerances"]["OH_Line"]["seismic"]) < float(seismic_risk):
                                db.edit_edge_status(edge[0].lstrip(), availability=0, file_name=e_file)
                    elif type_of_edge == "UG_Line":
                        logging.info("automatic event upon UG Line")
                        if float(settings["tolerances"]["UG_Line"]["wind"]) < float(wind_risk) or float(settings["tolerances"]["OH_Line"]["water"]) < float(water_risk) or float(settings["tolerances"]["OH_Line"]["fire"]) < float(fire_risk) or float(settings["tolerances"]["OH_Line"]["seismic"]) < float(seismic_risk):
                                db.edit_edge_status(edge[0].lstrip(), availability=0, file_name=e_file)
                    elif type_of_edge == "switch":
                        logging.info("automatic event upon switch")
                        if float(settings["tolerances"]["switch"]["wind"]) < float(wind_risk) or float(settings["tolerances"]["OH_Line"]["water"]) < float(water_risk) or float(settings["tolerances"]["OH_Line"]["fire"]) < float(fire_risk) or float(settings["tolerances"]["OH_Line"]["seismic"]) < float(seismic_risk):
                                db.edit_edge_status(edge[0].lstrip(), availability=0, file_name=e_file)
                    elif type_of_edge == "transformer":
                        logging.info("automatic event upon transformer")
                        if float(settings["tolerances"]["transformer"]["wind"]) < float(wind_risk) or float(settings["tolerances"]["OH_Line"]["water"]) < float(water_risk) or float(settings["tolerances"]["OH_Line"]["fire"]) < float(fire_risk) or float(settings["tolerances"]["OH_Line"]["seismic"]) < float(seismic_risk):
                                db.edit_edge_status(edge[0].lstrip(), availability=0, file_name=e_file)



            # Keep a local copy of repair file
            from shutil import copy
            repair_file = gv.project["data"]["repair"]
            dst = os.path.join(os.getcwd(), 'repair-file.csv')
            copy(repair_file, dst)

            # Keep a local copy of edge file

            last_modified_edge_file = gv.filepaths["edges"]
            # edge_file_at_this_time_stamp = os.path.join(newpath, 'edge-file.csv')
            # dst = os.path.join(os.getcwd(), 'edge-file.csv')
            # copy(last_modified_edge_file, dst)

    else:
        print("[x] did not find node file. This operation will not work.")
        return False

def collect_time_series_data_across_folders(simulation_folder, startime="", stoptime="", interval=""):

    # datetime_obj = datetime.strptime(startime, "%m/%d/%Y %H:%M")
    # month_value = "{:02d}".format(datetime_obj.month)
    # temp_folder_name = str(datetime_obj.year) + month_value + str(datetime_obj.day) + str(datetime_obj.hour) + str(
    #     datetime_obj.minute) + str(datetime_obj.second)

    subfolders = [f.name for f in os.scandir(simulation_folder) if f.is_dir()]
    for s in subfolders:
        timestring = reverse_time_step(s)
        print("[i] Performing event simulation for time-step {}".format(timestring))
        logging.info("Performing event simulation for time-step {}".format(timestring))
        automatic_impact_of_event(simulation_folder, s)

    if gv.timeseries_data_created is True:
        cncf = open("complete_nodal_calculation_file.csv", "a+")  # cncf = complete_nodal_calculation_file
    else:
        cncf = open("complete_nodal_calculation_file.csv", "w+")






def create_timeseries_data(timeseries_dict, vary_load=True, vary_gen=False, vary_criticality=False):
    """

    :param timeseries_dict:
    :param vary_gen:
    :param vary_criticality:
    :return:
    """
    t = datetime.now()
    month_value = "{:02d}".format(t.month)
    hour_value = "{:02d}".format(t.hour)
    simulation_folder_name = "ts_" + str(t.year) + "_" + month_value + "_" + str(t.day) + "_" + hour_value + "_" + str(t.minute) + "_" + str(t.second)
    logging.info("timeseries_simulation function is called")

    df = pd.read_csv(timeseries_dict["load_profile"], skipinitialspace=True)
    # what columns are there in the file:
    fields = list(df)
    df = pd.read_csv(timeseries_dict["load_profile"], skipinitialspace=True, usecols=fields)
    threatfile = timeseries_dict["threat_profile"]

    size = df.shape

    if vary_gen is True:
        if "generation" in timeseries_dict:
            df_gen = pd.read_csv(timeseries_dict["generation"], skipinitialspace=True)
        else:
            print("No generation shape timeseries file found.")
            logging.error("No generation shape timeseries file found.")
            continue_sim = input("[?] Do you want to continue the simulation any way without generator data? [Y/N]\n[>] ")
            if continue_sim.lstrip().lower() == "y" or "yes":
                vary_gen = False
            else:
                logging.error("No generation shape timeseries file found. FileNotFoundError will be raised.")
                raise FileNotFoundError

    cwd = os.getcwd()

    newpath = os.path.join(cwd, simulation_folder_name)
    if not os.path.exists(newpath):
        os.mkdir(newpath)
    os.chdir(newpath)

    main_working_dir = os.getcwd()

    for r in range(1, size[1]):
        timestamp = fields[0]
        colname = fields[r]
        for q in range(1, size[0]):
            datetime_obj = datetime.strptime(df[timestamp][q], "%m/%d/%Y %H:%M")
            month_value = "{:02d}".format(datetime_obj.month)
            day_value = "{:02d}".format(datetime_obj.day)
            hour_value = "{:02d}".format(datetime_obj.hour)
            minute_value = "{:02d}".format(datetime_obj.minute)
            second_value = "{:02d}".format(datetime_obj.second)
            temp_folder_name = str(datetime_obj.year) + month_value + day_value + hour_value + minute_value + second_value
            cwd = os.getcwd()
            newpath = os.path.join(cwd, temp_folder_name)
            if not os.path.exists(newpath):
                os.mkdir(newpath)
            os.chdir(newpath)
            # print(str(df[colname][q]))
            if vary_load is True:
                create_timestamped_node_file(colname, new_load=str(df[colname][q]))
            if vary_gen is True:
                create_timestamped_node_file(colname, new_gen=str(df_gen[colname][q]))

            # Find the corresponding threat file and copy it here
            create_threatfile(threatfile, df[timestamp][q])
            modify_edge_file()
            # Go back to upper directory level
            gv.main_working_dir = main_working_dir
            os.chdir(main_working_dir)

    return main_working_dir





