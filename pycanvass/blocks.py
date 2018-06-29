"""
A generic class for edges and nodes, and their status, so that all components can be
manipulated in run-time.
"""

import json
import csv
import pycanvass.global_variables as gv
import os
import pycanvass.complexnetwork as cn
import logging
from shutil import copyfile


def set_simulation_folder(projectname):
    cwd = os.getcwd()
    newpath = os.path.join(cwd, projectname)
    if not os.path.exists(newpath):
        os.mkdir(newpath)
        os.mkdir(newpath)


def load_repair(filename=""):
    """

    :param filename:
    :return:
    """
    if filename == "":
        repair_file = gv.project["data"]["repair"]
    else:
        repair_file = filename

    with open(repair_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)  # Rewind.
        repairs = csv.reader(f)
        if has_header:
            next(repairs)  # Skip header row

        for repair in repairs:
            repairer_name = repair[0]
            repair_obj = Repair(base_name=repair[0],
                                lat=repair[1],
                                long=repair[2],
                                crew=repair[3],
                                pole=repair[4],
                                line=repair[6],
                                transformer=repair[5],
                                handpump=repair[7],
                                switches=repair[8],
                                mobile_genset=repair[9]
                                )

            gv.repair_dict[repairer_name] = repair_obj

    if len(gv.repair_dict) == 0:
        logging.info("No repair crew found")
        print("[i] No repair crew found")
    else:
        logging.info('%d repair crew bases will be used in the simulation' % len(gv.repair_dict))


def load_threats(filename=""):
    """
    Creates objects of all the threat nodes
    :param filename:
    :return: threat_dict: Dictionary containing all the threat objects.
    """
    if filename == "":
        threat_file = gv.project["data"]["threats"]
    else:
        threat_file = filename

    with open(threat_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)  # Rewind.
        threats = csv.reader(f)
        if has_header:
            next(threats)  # Skip header row

        for threat in threats:
            threat_name = threat[0]
            threat_obj = Threat(anchor=threat[0],
                                lat=threat[1],
                                long=threat[2],
                                strength=threat[3],
                                water_risk=threat[4],
                                fire_risk=threat[6],
                                wind_risk=threat[5],
                                seismic_risk=threat[7],
                                duration=threat[8]
                                )

            gv.threat_dict[threat_name] = threat_obj
    if len(gv.threat_dict) == 0:
        print("[i] No threat anchor points. We will use generic settings and default values.")
        logging.info('No threat anchor points will be used in the simulation.')
    else:
        logging.info('%d threat anchor points will be used in the simulation.' % len(gv.threat_dict))


def rebuild():
    edge_file = gv.project["data"]["edges"]
    gv.filepaths["edges"] = edge_file

    node_file = gv.project["data"]["nodes"]
    gv.filepaths["nodes"] = node_file

    edge_dict = {}
    node_dict = {}

    with open(edge_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)  # Rewind.
        edges = csv.reader(f)
        if has_header:
            next(edges)  # Skip header row
        number = 1
        for edge in edges:
            edge_name = edge[0].lstrip()
            edge_obj = Edge(name=edge[0],
                            kind=edge[1],
                            from_node=edge[2],
                            to_node=edge[3],
                            status=edge[4].lstrip(),
                            r=edge[5], x=edge[6], b=edge[7],
                            fire_risk=edge[8],
                            wind_risk=edge[9],
                            water_risk=edge[10],
                            rating=edge[11],
                            hardening=edge[12])

            edge_dict[edge_name] = edge_obj
            number = number + 1

    # Making the nodes dictionary:

    with open(node_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        nodes = csv.reader(f)
        if has_header:
            next(nodes)  # Skip header row

        for node in nodes:
            node_name = node[0].lstrip()
            node_obj = Node(name=node[0],
                            phase=node[1],
                            lat=node[2],
                            long=node[3],
                            voltage=node[4],
                            load=node[5],
                            gen=node[6],
                            kind=node[7],
                            critical=node[8],
                            category=node[9])

            node_dict[node_name] = node_obj

    rebuilt_network_dict = cn.build_network(node_dict, edge_dict)
    return rebuilt_network_dict

def load_project_ts():
    """

    :return:
    """
    """
        Creates the JSON object that has all the parameters users can modify to customize the project
        :param filename:
        :return: JSON object
        """
    filename = gv.filepaths["model"]
    project_file = open(filename)
    gv.project = json.load(project_file)
    gv.user_timezone = gv.project["timezone"]
    project_file.close()
    which_dir = os.getcwd()
    # print("[i] Loading Node and Edge file from folder {}".format(which_dir))
    edge_file = "edge-file.csv"
    node_file = "node-file.csv"
    threat_file = "threat-file.csv"
    repair_file = "repair-file.csv"

    continue_simulation = True

    if os.path.isfile(node_file) and os.path.isfile(edge_file) and os.path.isfile(threat_file) and os.path.isfile(repair_file):
        continue_simulation = True
        logging.info("[i] Did find all the required files")
    else:
        print("[x] Edge file not found. Simulation will not be completed. ")
        logging.info("Edge file not found. Simulation will not be completed. ")
        continue_simulation = False
        return

    metric_file = gv.project["resiliency_metric"]["algorithm"]
    gv.filepaths["metric"] = metric_file

    edge_dict = {}
    node_dict = {}

    # Making the edges dictionary here:

    with open(edge_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)  # Rewind.
        edges = csv.reader(f)
        if has_header:
            next(edges)  # Skip header row
        number = 1
        for edge in edges:
            edge_name = str(edge[0])
            edge_obj = Edge(name=edge[0],
                            kind=edge[1],
                            from_node=edge[2],
                            to_node=edge[3],
                            status=edge[4],
                            r=edge[5], x=edge[6], b=edge[7],
                            fire_risk=edge[8],
                            wind_risk=edge[9],
                            water_risk=edge[10],
                            rating=edge[11],
                            hardening=edge[12],
                            availability=edge[13])

            edge_dict[edge_name] = edge_obj
            number = number + 1

    # Making the nodes dictionary:

    with open(node_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        nodes = csv.reader(f)
        if has_header:
            next(nodes)  # Skip header row

        for node in nodes:
            node_name = node[0]
            node_obj = Node(name=node[0],
                            phase=node[1],
                            lat=node[2],
                            long=node[3],
                            voltage=node[4],
                            load=node[5],
                            gen=node[6],
                            kind=node[7],
                            critical=node[8],
                            category=node[9],
                            backup_dg=node[10],
                            wind_cc=node[11],
                            water_cc=node[12],
                            seismic_cc=node[13],
                            fire_cc=node[14],
                            preexisting_damage=node[15],
                            availability=node[16],
                            foliage=node[17],
                            mttr=node[18],
                            op_cost=node[19],
                            repair_cost=node[20]
                            )

            node_dict[node_name] = node_obj

    load_threats()
    load_repair()

    for key, value in node_dict.items():
        gv.obj_nodes.append(value)

    for key, value in edge_dict.items():
        gv.obj_edges.append(value)

    return node_dict, edge_dict


def load_project():
    """
    Creates the JSON object that has all the parameters users can modify to customize the project
    :param filename:
    :return: JSON object
    """

    gv.timeseries_data_created = False


    filename = gv.filepaths["model"]
    project_file = open(filename)
    gv.project = json.load(project_file)
    project_file.close()

    # keep node backup copy
    from shutil import copyfile

    # keep edge backup copy

    edge_file = gv.project["data"]["edges"]
    gv.filepaths["edges"] = edge_file
    try:
        if os.path.isfile(edge_file):
            temp = os.path.basename(edge_file)
            filename = os.path.splitext(temp)[0]
            edge_backup_filename = filename + "-backup.csv"
    except:
        logging.error("Failed to create backup files")

    node_file = gv.project["data"]["nodes"]
    gv.filepaths["nodes"] = node_file

    metric_file = gv.project["resiliency_metric"]["algorithm"]
    gv.filepaths["metric"] = metric_file

    edge_dict = {}
    node_dict = {}

    # set_simulation_folder(gv.project["project_name"])
    # Making the edges dictionary here:

    with open(edge_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)  # Rewind.
        edges = csv.reader(f)
        if has_header:
            next(edges)  # Skip header row
        number = 1
        for edge in edges:
            edge_name = str(edge[0])
            edge_obj = Edge(name=edge[0],
                            kind=edge[1],
                            from_node=edge[2],
                            to_node=edge[3],
                            status=edge[4],
                            r=edge[5], x=edge[6], b=edge[7],
                            fire_risk=edge[8],
                            wind_risk=edge[9],
                            water_risk=edge[10],
                            rating=edge[11],
                            hardening=edge[12],
                            availability=edge[13])

            edge_dict[edge_name] = edge_obj
            number = number + 1

    # Making the nodes dictionary:

    with open(node_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        nodes = csv.reader(f)
        if has_header:
            next(nodes)  # Skip header row

        for node in nodes:
            node_name = node[0]
            node_obj = Node(name=node[0],
                            phase=node[1],
                            lat=node[2],
                            long=node[3],
                            voltage=node[4],
                            load=node[5],
                            gen=node[6],
                            kind=node[7],
                            critical=node[8],
                            category=node[9],
                            backup_dg=node[10],
                            wind_cc=node[11],
                            water_cc=node[12],
                            seismic_cc=node[13],
                            fire_cc=node[14],
                            preexisting_damage=node[15],
                            availability=node[16],
                            foliage=node[17],
                            mttr=node[18],
                            op_cost=node[19],
                            repair_cost=node[20]
                            )

            node_dict[node_name] = node_obj

    load_threats()
    load_repair()

    for key, value in node_dict.items():
        gv.obj_nodes.append(value)

    for key, value in edge_dict.items():
        gv.obj_edges.append(value)

    return gv.project, node_dict, edge_dict


def make_edges(filename):
    """
    Returns a dictionary of all edges made from available data
    :param filename:
    :return:
    """
    Edges = {}
    with open(filename) as f:
        edges = csv.reader(f)
        for edge in edges:
            edge_name = edge[0].lstrip()
            edge_obj = Edge(name=edge[0],
                            kind=edge[1],
                            from_node=edge[2],
                            to_node=edge[3],
                            status=edge[4],
                            r=edge[5], x=edge[6], b=edge[7],
                            fire_risk=edge[8],
                            wind_risk=edge[9],
                            water_risk=edge[10],
                            rating=edge[11],
                            hardening=edge[12],
                            availability=edge[13])

            Edges[edge_name] = edge_obj

    return Edges


class Repair:
    """
    Threat anchors are the locations where an impact of any event is most likely to be experienced
    """

    def __init__(self, base_name, lat, long, crew, pole, line, transformer, handpump, switches, mobile_genset):
        self.base_name = base_name
        self.lat = lat
        self.long = long
        self.crew = crew
        self.pole = pole
        self.line = line
        self.transformer = transformer
        self.handpump = handpump
        self.switches = switches
        self.mobile_genset = mobile_genset


class Threat:
    """
    Threat anchors are the locations where an impact of any event is most likely to be experienced
    """

    def __init__(self, anchor, lat, long, strength, water_risk, fire_risk, wind_risk, seismic_risk, duration):
        self.anchor = anchor
        self.lat = lat
        self.long = long
        self.strength = strength
        self.water_risk = water_risk
        self.fire_risk = fire_risk
        self.wind_risk = wind_risk
        self.seismic_risk = seismic_risk
        self.duration = duration


class Edge:
    """
    Edges include transformers, overhead Lines, underground Lines, switches, fuses, reclosers, etc.
    """
    numberOfEdges = 0
    allEdges = []

    def __init__(self, name, kind, from_node, to_node, status, r, x, b, wind_risk, water_risk, fire_risk, rating,
                 hardening, availability):
        """
        constructor method
        """
        self.name = name
        self.kind = kind
        self.from_node = from_node
        self.to_node = to_node
        self.status = status  # status: normal status. If Normally Open, status = 1; If Normally Closed, status = 0
        self.r = r  # resistance:
        self.x = x  # impedance:
        self.b = b
        self.wind_risk = wind_risk
        self.water_risk = water_risk
        self.fire_risk = fire_risk
        self.rating = rating
        self.hardening = hardening
        self.availability = availability

        Edge.numberOfEdges += 1
        Edge.allEdges.append(self)

    def count_edges(self):
        """
        Count the number of edges that has been created in the program
        :return:
        """
        print(self.numberOfEdges)


class Node:
    """
    Nodes include all generators, poles, loads, meters, etc.
    """

    numberOfNodes = 0  # Number of all nodes in the network
    allNodes = []  # Collection of all nodes in the network

    def __init__(self, name, phase, lat, long, voltage, load, gen, kind, critical, category, backup_dg, wind_cc,
                 water_cc, seismic_cc, fire_cc, preexisting_damage, availability, foliage, mttr, op_cost, repair_cost):
        self.name = name
        self.phase = phase
        self.lat = lat
        self.long = long
        self.voltage = voltage
        self.load = load
        self.gen = gen
        self.kind = kind
        self.critical = critical
        self.category = category
        self.backup_dg = backup_dg
        self.wind_cc = wind_cc
        self.water_cc = water_cc
        self.seismic_cc = seismic_cc
        self.fire_cc = fire_cc
        self.preexisting_damage = preexisting_damage
        self.availability = availability
        self.foliage = foliage
        self.mttr = mttr
        self.op_cost = op_cost
        self.repair_cost = repair_cost

        Node.numberOfNodes += 1
        Node.allNodes.append(self)

    def count_nodes(self):
        """
        Count the number of nodes that has been created in the program
        :return:
        """
        print(self.numberOfNodes)
