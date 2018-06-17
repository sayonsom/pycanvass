"""
This library does all the complex network analysis required by the program
"""
# from typing import List, Any, Tuple, Dict, Union
import inspect
import csv
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import json
import random
from pycanvass.all import *
import pycanvass.global_variables as gv
import sys
import pycanvass.utilities as util
import time
import datetime
import os
from pathlib import Path

from networkx import Graph

attempts = 0
settings = ""


def _input_user_pref_file():
    util._banner()
    current_folder_path, current_folder_name = os.path.split(os.getcwd())
    wd = current_folder_path + "\\" + current_folder_name + "\\"
    print("[i] Current working folder: {}".format(wd))
    default_json_file_name = current_folder_path + "\\" + current_folder_name + "\\user_preferences.json"
    default_json_file_name = Path(default_json_file_name)

    if default_json_file_name.exists():
        print("[i] Loaded default user preferences file: {}".format(default_json_file_name))
        # time.sleep(0.5)
        user_preference_path = default_json_file_name
    else:
        print("[x] Default user preferences file not found.")
        user_preference_path = input("\n[i] Please enter the path to your user-preferences file (*.JSON):\n")

    return str(user_preference_path)


while attempts < 4:
    if attempts == 3:
        break
    try:
        user_preference_path = _input_user_pref_file()
        u_settings = open(user_preference_path)
        settings = json.load(u_settings)
        u_settings.close()
        break
    except:
        print("[x] Could not get the user preference file.")
        attempts += 1
        if attempts == 3:
            print("[x] Failed to configure user preferences correctly.")
            sys.exit()
        elif attempts == 2:
            print("[i] One more chance to get the user preference correctly setup.")


# ---------------------------


# # #
# A #
# # #

def add_node_attr(graph):
    """
    Add all the details about the nodes here
    :param graph:
    :return: dictionary containing node features
    """
    all_nodes = graph.nodes()
    n_file = gv.filepaths["nodes"]

    for n in all_nodes:
        node_search_result = _node_search(n)
        try:
            with open(n_file, 'r') as f:
                csvr = csv.reader(f)
                csvr = list(csvr)
                for row in csvr:
                    if row[0].lstrip() == n:
                        if node_search_result is not 0:
                            graph.node[n]['type'] = row[9].lstrip()
                            graph.node[n]['gen'] = row[6].lstrip()
                            graph.node[n]['demand'] = row[5].lstrip()
                            graph.node[n]['lat'] = row[2].lstrip()
                            graph.node[n]['long'] = row[3].lstrip()

        except:
            print("[x] Error in setting up the node attributes. ")
            called_from = inspect.stack()[1]
            called_module = inspect.getmodule(called_from[0])
            logging.error("[x] Called from - {} : Node attributes could not be set.".format(called_module, e))


# # #
# N #
# # #


def _node_search(n):
    n_file = gv.filepaths["nodes"]
    with open(n_file) as f:
        counter = 0
        match_flag = 0
        nodes = csv.reader(f)
        for node in nodes:
            counter += 1
            if node[0].lstrip() == n:
                match_flag = 1
                return counter - 1

        if match_flag == 0:
            called_from = inspect.stack()[1]
            called_module = inspect.getmodule(called_from[0])
            logging.error("[x] Called from - {} : Node {} could not be found.".format(called_module, e))
            return 0


# # #
# B #
# # #


def build_network(node_dict, edge_dict):
    """

    :param node_dict:
    :param edge_dict:
    :return: network_dict: Dictionary containing several network graph objects, and edge details
             network_dict["normal"] : Normal network topology
             network_dict["total"] : Graph containing self-loops, including reconfiguration options
             network_dict["n_open"]: List of all edges which are normally open
             network_dict["n_closed"] : List of all edges which are normally closed
    """

    network_dict = {}

    gv.obj_nodes = []
    gv.obj_edges = []

    for key, value in node_dict.items():
        gv.obj_nodes.append(value)

    for key, value in edge_dict.items():
        gv.obj_edges.append(value)

    graph = nx.Graph()
    total_graph = nx.DiGraph()

    for key, value in node_dict.items():
        gv.obj_nodes.append(value)

    for key, value in edge_dict.items():
        gv.obj_edges.append(value)

    for edge in gv.obj_edges:
        total_graph.add_edge(edge.from_node.lstrip(), edge.to_node.lstrip())
        if edge.status.lstrip() != "0" and edge.availability.lstrip() != "0":
            graph.add_edge(edge.from_node.lstrip(), edge.to_node.lstrip())
            gv.closed_edges_list.append(tuple((edge.from_node.lstrip(), edge.to_node.lstrip())))
        else:
            gv.open_edges_list.append(tuple((edge.from_node.lstrip(), edge.to_node.lstrip())))

    logging.info("Populating nodes and edges with values")

    for n in gv.obj_nodes:
        graph.node[n.name]['name'] = n.name
        graph.node[n.name]['load'] = n.load
        graph.node[n.name]['gen'] = n.gen
        graph.node[n.name]['lat'] = n.lat
        graph.node[n.name]['long'] = n.long
        graph.node[n.name]['kind'] = n.kind
        graph.node[n.name]['critical'] = n.critical

        total_graph.node[n.name]['name'] = n.name
        total_graph.node[n.name]['load'] = n.load
        total_graph.node[n.name]['gen'] = n.gen
        total_graph.node[n.name]['lat'] = n.lat
        total_graph.node[n.name]['long'] = n.long
        total_graph.node[n.name]['kind'] = n.kind
        total_graph.node[n.name]['critical'] = n.critical

        try:
            if n.kind.upper() == "PV" or n.kind.upper() == "SWING":
                gv.all_sources[n.name] = n.gen
            else:
                try:
                    gv.all_loads[n.name] = n.load
                    if int(n.critical) > 5:
                        gv.all_critical_loads[n.name] = n.load
                except ValueError:
                    logging.error("No loads found in the network while making the graph.")
        except ValueError:
            logging.error("No power resource found in the network while making the graph.")

    gv.graph_collection.append(graph)
    gv.graph_collection.append(total_graph)

    for g in gv.graph_collection:
        for e in gv.obj_edges:
            try:
                g[e.from_node.lstrip()][e.to_node.lstrip()]['water_risk'] = e.water_risk
                gv.water_risk_values.append(e.water_risk.lstrip())
            except KeyError:
                logging.info("No edge between %s and %s, so no water risk" % (e.from_node.lstrip(), e.to_node.lstrip()))
                gv.water_risk_values.append(0)

            try:
                g[e.from_node.lstrip()][e.to_node.lstrip()]['wind_risk'] = e.wind_risk
                gv.wind_risk_values.append(e.wind_risk.lstrip())
            except KeyError:
                logging.info(
                    "[i] No edge between %s and %s, so no wind risk " % (e.from_node.lstrip(), e.to_node.lstrip()))
                gv.wind_risk_values.append(0)

            try:
                g[e.from_node.lstrip()][e.to_node.lstrip()]['fire_risk'] = e.fire_risk
                gv.fire_risk_values.append(e.fire_risk.lstrip())
            except KeyError:
                logging.info(
                    "[i] No edge between %s and %s, so no fire risk " % (e.from_node.lstrip(), e.to_node.lstrip()))
                gv.fire_risk_values.append(0)

    network_dict["normal"] = graph
    network_dict["total"] = total_graph
    network_dict["n_open"] = gv.open_edges_list
    network_dict["n_closed"] = gv.closed_edges_list

    return network_dict


# # #
# C #
# # #


def _create_pos_dictionary(graph):
    """
    Internal function, that creates a dictionary that contains position of all nodes in the network
    :param graph:
    :return: dictionary of all nodes with their geo-coordinates,
             dictionary with little shifted position for showing labels
    """
    nodes = graph.nodes()  # list of all nodes <-- keys
    pos_dictionary = {}  # initializing a dictionary to hold the positions
    label_pos_dictionary = {}
    for n in nodes:
        pos_dictionary[n] = tuple((float(graph.node[n]['long']), float(graph.node[n]['lat'])))
        label_pos_dictionary[n] = tuple((float(graph.node[n]['lat']), float(graph.node[n]['long'])))

    return pos_dictionary, label_pos_dictionary


# # #
# F #
# # #

def feeder_path(graph, from_node, to_node):
    """
    :param graph: NetworkX graph object
    :param from_node:
    :param to_node:
    :return: all restoration paths from generator to load nodes
    """
    path_graph = nx.Graph()
    paths = nx.all_simple_paths(graph, from_node, to_node)

    return paths


# # #
# L #
# # #

def lat_long_layout(graph, show=False, save=True, title="Visualization"):
    """
    Help visualize the network graph and some of its resilience properties.
    If your graph does not come with
    :param graph:
    :param show: (Default is False)
    :param save: (Default is True)
    :return:
    """
    focus = "impact_on_edge"
    logging.info(
        "Lat_long_layout function used, focus = {}, trying to display = {}, saving = {}".format(focus, show, save))

    try:
        pos, label_pos = _create_pos_dictionary(graph)
    except ValueError:
        print("[x] Error: Could not create determine where to put the nodes and edges. "
              "... Please check the lat, longs of your nodes. "
              ""
              "... In case your file does not have the lat, longs, generate"
              "... random lat-longs by using the layout_model(<model.glm>, map_random=True) function."
              ""
              "... Please read the documentation on how to do that. ")

        logging.error('Could not create the dictionary for pos, or label_pos')

    color_scheme = settings['visualization']['color_scheme']

    values = []

    for e in graph.edges():
        try:
            values.append(graph[str(e[0])][str(e[1])][focus])
        except:
            values.append(1)

    color_scheme = plt.get_cmap(color_scheme)
    c_norm = colors.Normalize(vmin=0, vmax=7)
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=color_scheme)
    color_list = []
    edge_labels = nx.get_edge_attributes(graph, focus)

    for i in range(len(values)):
        color_val = scalar_map.to_rgba(float(values[i]))
        color_list.append(color_val)

    # add a connection to a web visualization

    nx.draw_networkx_edges(graph,
                           pos=pos,
                           edge_color=color_list,
                           # style='dashed',
                           width=2.0)

    nx.draw_networkx_nodes(graph,
                           pos=pos,
                           nodelist=graph.nodes(),
                           node_color='b',
                           node_shape='x')

    nx.draw_networkx_labels(graph,
                            pos=label_pos,
                            edge_labels=edge_labels)

    if show:
        plt.title(title)
        plt.show()

    if save:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')
        filename = "visualization_" + st + ".png"
        plt.savefig(filename)


def loads(critical=False):
    """
    This function lists the loads in the power system network.
    :param critical: Default value is set to False, which means all loads will be displayed in the network.
                     Set this value to True to see only the critical loads
    :return: gv.all_loads or gv.all_critical_loads
    """
    if not critical:
        return gv.all_loads
    else:
        return gv.all_critical_loads


# # #
# M #
# # #


def make_graph(all_edges):
    """

    :param all_edges: List of all instances of Edge objects created by the program
    :return: graph: NetworkX graph object,
             normally_open_edges: number of open edges, that can be closed later if necessary
    """
    graph = nx.Graph()
    total_graph = nx.Graph()

    for edge in all_edges:
        total_graph.add_edge(edge.from_node, edge.to_node)
        if edge.status != "0":
            graph.add_edge(edge.from_node, edge.to_node)
            gv.closed_edges_list.append(tuple((edge.from_node, edge.to_node)))
        else:
            gv.open_edges_list.append(tuple((edge.from_node, edge.to_node)))

    return graph, total_graph, gv.open_edges_list, gv.closed_edges_list


def make_path_graph(nodelist, **kwargs):
    """
    Create a graph based on a found path between a source and a generator
    :param nodelist:
    :return: path_graph: A NetworkX object that is a single path's graph, that can be further used for resiliency
                         analysis

    """

    path_graph = nx.Graph()
    i = 0
    while i < len(nodelist) - 1:
        path_graph.add_edge(nodelist[i], nodelist[i + 1])
        i += 1

    return path_graph


# # #
# P #
# # #


def preprocess(graph, node_dict, edge_dict):
    """

    :param graph:
    :param node_dict:
    :param edge_dict:
    :return:
    """

    gv.obj_nodes = []
    gv.obj_edges = []
    for key, value in node_dict.items():
        gv.obj_nodes.append(value)

    for key, value in edge_dict.items():
        gv.obj_edges.append(value)

    print("[i] Attempting to populate nodes and edges with values")

    for n in gv.obj_nodes:
        graph.node[n.name]['name'] = n.name
        graph.node[n.name]['load'] = n.load
        graph.node[n.name]['gen'] = n.gen
        graph.node[n.name]['lat'] = n.lat
        graph.node[n.name]['long'] = n.long
        graph.node[n.name]['kind'] = n.kind
        graph.node[n.name]['critical'] = n.critical

        try:
            if n.kind.upper() == "PV" or n.kind.upper() == "SWING":
                gv.all_sources[n.name] = n.gen
            else:
                try:
                    gv.all_loads[n.name] = n.load
                    if int(n.critical) > 5:
                        gv.all_critical_loads[n.name] = n.load
                except ValueError:
                    logging.error("No loads found in the network, while making the graph.")
        except ValueError:
            logging.error("No power resource found in the network, while making the graph.")

    for e in gv.obj_edges:
        try:
            graph[e.from_node][e.to_node]['water_risk'] = e.water_risk
            gv.water_risk_values.append(e.water_risk)
        except KeyError:
            print("[i] No edge between %s and %s exist in this topology." % (e.from_node, e.to_node))
            gv.water_risk_values.append(0)

        try:
            graph[e.from_node][e.to_node]['wind_risk'] = e.wind_risk
            gv.water_risk_values.append(e.wind_risk)
        except KeyError:
            print("[i] No edge between %s and %s exist in this topology." % (e.from_node, e.to_node))
            gv.water_risk_values.append(0)

        try:
            graph[e.from_node][e.to_node]['fire_risk'] = e.fire_risk
            gv.water_risk_values.append(e.fire_risk)
        except KeyError:
            print("[i] No edge between %s and %s exist in this topology." % (e.from_node, e.to_node))
            gv.water_risk_values.append(0)


# # #
# R #
# # #


def resiliency_downstream(graph, edgelist, event):
    """
    This function computes the resiliency of all downstream sections,
    mainly looking out for critical loads
    :param graph:
    :param edgelist: All downstream sections of the feeder, from perspective of an edge being analyzed
    :param event: dictionary describing the event magnitude
    :return:
    """

    risk_dict = {}

    for e in edgelist:
        for oe in gv.obj_edges:
            if e[0].lstrip() == oe.from_node.lstrip() and e[1].lstrip() == oe.to_node.lstrip():
                risk_dict[tuple((e[0], e[1]))] = (event["water_risk"] * float(oe.water_risk.lstrip())
                                                  + event["wind_risk"] * float(oe.wind_risk.lstrip())
                                                  + event["fire_risk"] * float(oe.fire_risk.lstrip())) / 30

    print("Risk per edge -->")
    print(risk_dict)

    # loads encountered

    # critical loads encountered

    # generators encountered

    # switches encountered

    pass


def resiliency_upstream(graph, edgelist, event):
    """
    This function computes the resiliency of all upstream sections,
    mainly looking out for generators
    :param edgelist: All upstream sections of the feeder, from persective of a feeder being analyzed
    :return:
    """
    print("Heat your ", edgelist)
    pass


def resiliency(analysis='nodal'):
    """
    This function helps compute the resiliency metric of the network of a
    node, or a network
    :param kwargs:
    :return:
    """

    # 0. what's the event?

    event = gv.event

    # 1. get the graphs

    g1 = gv.graph_collection[0]
    g2 = gv.graph_collection[1]
    nodes = g2.nodes()
    edges = g2.edges()

    # 2. for which node and edge are you doing the analysis?
    wg = nx.DiGraph()  # wg: working graph
    wg.add_edges_from(edges)

    for n in nodes:
        # Finding Downstream Edges
        print("Downstream Edges of %s -->" % n)
        downstream_edges = list(nx.dfs_edges(wg, n))
        resiliency_downstream(g2, downstream_edges, event)

        # Finding Upstream Edges
        print("Upstream Edges of %s -->" % n)
        upstream_edges = list(nx.edge_dfs(wg, n, orientation='reverse'))
        resiliency_upstream(g2, upstream_edges, event)

    # 3. track back from that edge to a source, or multiple sources


# # #
# S #
# # #


def sources():
    """
    This is a querying function that lists the power resources in a network
    :return: list of all power sources within a network
    """
    return gv.all_sources


def simple_show(graph):
    """
    Display the simple network representation of the graph
    :param graph: NetworkX graph object
    :return:
    """
    nx.draw(graph)
    plt.show()


def summary(graph):
    """
    Summarize all the important graph topological properties
    :param graph:
    :return:
    """
    temp_dict = {'degree_centrality': nx.degree_centrality(graph),
                 'betweeness': nx.betweenness_centrality(graph),
                 'resistance_centrality': nx.current_flow_closeness_centrality(graph)}

    return temp_dict

# # #
# V #
# # #
