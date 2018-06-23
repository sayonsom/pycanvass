from pycanvass.data_bridge import _node_search
import pycanvass.global_variables as gv
# import pycanvass.resiliency as res
# import pycanvass.blocks as blocks
import re
import csv
import pandas as pd
import logging
# import pycanvass.complexnetworks as cn
import os
from datetime import *


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

    node_search_result = _node_search(node_to_modify)
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


def search_timestamp_in_df(df, val):
    a = df.index[df['timestamp'].str.contains(val)]
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
    print(df.head())

    row_number = search_timestamp_in_df(df, timestamp)

    with open("threat-file-tmp.csv", "w+") as file:
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








def timeseries_simulation(start_time="", interval="", vary_load=True, vary_gen=False, vary_criticality=False):

    # For every time step, create a new folder, and a new node file.
    # in that same folder, create a corresponding threat file
    # create a corresponding edge file
    # create a corresponding repair file
    # perform resiliency nodal calculation

    pass



def modify_edge_file(timeseries_dict, vary_availability=True, vary_repairtime=False):
    """

    :param timeseries_dict:
    :param vary_gen:
    :param vary_criticality:
    :return:
    """
    t = datetime.now()
    month_value = "{:02d}".format(t.month)
    simulation_folder_name = "ts_" + str(t.year) + month_value + str(t.day) + str(t.hour) + str(t.minute) + str(t.second)
    logging.info("Time varying edge data will be included")

    df = pd.read_csv(timeseries_dict["edge_availability_curve"], skipinitialspace=True)
    # what columns are there in the file:
    fields = list(df)
    df = pd.read_csv(timeseries_dict["load_profile"], skipinitialspace=True, usecols=fields)
    size = df.shape

    if vary_repairtime is True:
        if "gen" in timeseries_dict:
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
            temp_folder_name = str(datetime_obj.year) + month_value + str(datetime_obj.day) + str(datetime_obj.hour) + str(datetime_obj.minute) + str(datetime_obj.second)
            cwd = os.getcwd()
            newpath = os.path.join(cwd, temp_folder_name)
            if not os.path.exists(newpath):
                os.mkdir(newpath)
            os.chdir(newpath)
            print(str(df[colname][q]))
            if vary_load is True:
                create_timestamped_node_file(colname, new_load=str(df[colname][q]))
            if vary_gen is True:
                create_timestamped_node_file(colname, new_gen=str(df_gen[colname][q]))

            os.chdir(main_working_dir)

def modify_node_file(timeseries_dict, vary_load=True, vary_gen=False, vary_criticality=False):
    """

    :param timeseries_dict:
    :param vary_gen:
    :param vary_criticality:
    :return:
    """
    t = datetime.now()
    month_value = "{:02d}".format(t.month)
    simulation_folder_name = "ts_" + str(t.year) + month_value + str(t.day) + str(t.hour) + str(t.minute) + str(t.second)
    logging.info("timeseries_simulation function is called")

    df = pd.read_csv(timeseries_dict["load_profile"], skipinitialspace=True)
    # what columns are there in the file:
    fields = list(df)
    df = pd.read_csv(timeseries_dict["load_profile"], skipinitialspace=True, usecols=fields)
    size = df.shape

    if vary_gen is True:
        if "gen" in timeseries_dict:
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
            temp_folder_name = str(datetime_obj.year) + month_value + str(datetime_obj.day) + str(datetime_obj.hour) + str(datetime_obj.minute) + str(datetime_obj.second)
            cwd = os.getcwd()
            newpath = os.path.join(cwd, temp_folder_name)
            if not os.path.exists(newpath):
                os.mkdir(newpath)
            os.chdir(newpath)
            print(str(df[colname][q]))
            if vary_load is True:
                create_timestamped_node_file(colname, new_load=str(df[colname][q]))
            if vary_gen is True:
                create_timestamped_node_file(colname, new_gen=str(df_gen[colname][q]))

            # Find the corresponding threat file and copy it here

            os.chdir(main_working_dir)







