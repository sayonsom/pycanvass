"""
A generic class for edges and nodes, and their status, so that all components can be
manipulated in run-time.
"""

import json
import csv
import pycanvass.global_variables as gv
import os
import pycanvass.complexnetwork as cn



def set_simulation_folder(projectname):
    cwd = os.getcwd()
    newpath = os.path.join(cwd,projectname)
    if not os.path.exists(newpath):
        os.mkdir(newpath)


def load_threats(filename):
    """
    Creates objects of all the threat nodes
    :param filename:
    :return: threat_dict: Dictionary containing all the threat objects.
    """
    threat_file = gv.project["data"]["threats"]

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
                                strength=threat[3])

            gv.threat_dict[threat_name] = threat_obj
    if len(gv.threat_dict) == 0:
        "No threat anchor points? Cool. We will use generic settings and default values."
    else:
        print('%d threat anchor points will be used in the simulation.' % len(gv.threat_dict))


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
                            category = node[9])

            node_dict[node_name] = node_obj

    rebuilt_network_dict = cn.build_network(node_dict, edge_dict)
    return rebuilt_network_dict


def load_project(filename):
    """
    Creates the JSON object that has all the parameters users can modify to customize the project
    :param filename:
    :return: JSON object
    """
    project_file = open(filename)
    gv.project = json.load(project_file)
    project_file.close()

    edge_file = gv.project["data"]["edges"]
    gv.filepaths["edges"] = edge_file

    node_file = gv.project["data"]["nodes"]
    gv.filepaths["nodes"] = node_file

    edge_dict = {}
    node_dict = {}

    set_simulation_folder(gv.project["project_name"])
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
                            category = node[9])

            node_dict[node_name] = node_obj

    load_threats(filename)
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
                            hardening=edge[12])

            Edges[edge_name] = edge_obj


    return Edges

class Threat:
    """
    Threat anchors are the locations where an impact of any event is most likely to be experienced
    """
    def __init__(self, anchor, lat, long, strength):
        self.anchor = anchor
        self.lat = lat
        self.long = long
        self.strength = strength


class Edge:
    """
    Edges include Transformers, OH Lines, Underground Lines,
    """
    numberOfEdges = 0
    allEdges = []

    def __init__(self, name, kind, from_node, to_node, status, r, x, b, wind_risk, water_risk, fire_risk, rating,
                 hardening):
        """
        constructor method
        """
        self.name = name
        self.kind = kind
        self.from_node = from_node
        self.to_node = to_node
        self.status = status      # status: normal status. If Normally Open, status = 1; If Normally Closed, status = 0
        self.r = r                # resistance:
        self.x = x                # impedance:
        self.b = b
        self.wind_risk = wind_risk
        self.water_risk = water_risk
        self.fire_risk = fire_risk
        self.rating = rating
        self.hardening = hardening

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

    numberOfNodes = 0           # Number of all nodes in the network
    allNodes = []               # Collection of all nodes in the network

    def __init__(self, name, phase, lat, long, voltage, load, gen, kind, critical, category):
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
        Node.numberOfNodes += 1
        Node.allNodes.append(self)

    def count_nodes(self):
        """
        Count the number of nodes that has been created in the program
        :return:
        """
        print(self.numberOfNodes)


