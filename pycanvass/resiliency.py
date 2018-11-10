import csv
import logging
import pprint
import sys
import json
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pycanvass.complexnetwork as cn
import pycanvass.data_bridge as db
import pycanvass.data_visualization as dv
import pycanvass.global_variables as gv

from networkx import DiGraph

pp = pprint.PrettyPrinter(indent=4)

global edge_status_list
edge_status_list = {}

global edge_switches
edge_switches = {}

u_settings = open(gv.filepaths['user_preferences'])
settings = json.load(u_settings)
u_settings.close()


def interdependent_network_connectivity():
    interdependent_network_connectivity_dict = {}
    interdependent_network_connectivity_dict["transport"] = 0.063  # <-- todo: Hard-coded, needs implementation
    return interdependent_network_connectivity_dict


def upstream_edge_info(wg, n):
    upstream_edges = list(nx.edge_dfs(wg, n, orientation='reverse'))
    # print(upstream_edges)
    up_switch_dict = {}
    e_file = gv.filepaths["edges"]
    for u in upstream_edges:
        # edge info:
        p = u[0].lstrip()
        q = u[1].lstrip()
        edge_of_path_name_1 = p + "_to_" + event_intensity(n)
        edge_of_path_name_2 = q + "_to_" + p
        edge_search_result_1 = db._edge_search(edge_of_path_name_1)
        edge_search_result_2 = db._edge_search(edge_of_path_name_2)
        try:
            with open(e_file, 'r') as f:
                csvr = csv.reader(f)
                csvr = list(csvr)
                for row in csvr:
                    if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                        if edge_search_result_1 != 0 or edge_search_result_2 != 0:
                            if row[1].lstrip() == "switch":
                                # print("[i] Upstream Switch: {}, Status: {}, Availability: {}".format(row[0], row[4],
                                # row[13]))
                                up_switch_dict[row[0]] = row[4]
                            if row[1].lstrip() == "transformer":
                                pass
                                # print(
                                # " [i] Upstream Transformer: {}, Status: {}, Availability: {}".format(row[0], row[4],
                                # row[13]))

        except:
            print("[x] Error in up-stream edge search.")
    return up_switch_dict


def lose_edge(from_node, to_node):
    # Normal graph
    g_normal = gv.graph_collection[0]
    cn.lat_long_layout(g_normal, show=True, save=False, title="Network in its current state")
    g_normal_damaged = nx.Graph()
    try:
        g_normal.remove_edge(from_node, to_node)
    except:
        print("[i] This edge in the normal graph may have been lost before. Moving on. ")
    g_normal_damaged.add_edges_from(g_normal.edges())
    cn.add_node_attr(g_normal_damaged)
    gv.graph_collection.append(g_normal_damaged)

    # Total graph
    g_total = gv.graph_collection[1]
    cn.lat_long_layout(g_total, show=True, save=False, title="All possible paths in the network")
    g_total_damaged = nx.DiGraph()
    try:
        g_total.remove_edge(from_node, to_node)
    except:
        print("[i] This edge in the complete graph may have been lost before. Moving on. ")
    g_total_damaged.add_edges_from(g_total.edges())
    cn.add_node_attr(g_total_damaged)
    gv.graph_collection.append(g_total_damaged)

    edge_of_path_name = from_node + "_to_" + to_node
    try:
        db.edit_edge_status(edge_of_path_name, set_status=0, availability=0)
    except:
        print("[i] Excel file could not be edited. It needs to be closed during the simulation.")

    return g_normal_damaged


def downstream_edge_info(wg, n):
    downstream_edges = list(nx.dfs_edges(wg, n))
    down_switch_dict = {}
    e_file = gv.filepaths["edges"]
    for d in downstream_edges:
        # edge info:
        p = d[0].lstrip()
        q = d[1].lstrip()
        edge_of_path_name_1 = p + "_to_" + q
        edge_of_path_name_2 = q + "_to_" + p
        edge_search_result_1 = db._edge_search(edge_of_path_name_1)
        edge_search_result_2 = db._edge_search(edge_of_path_name_2)
        # try:
        with open(e_file, 'r+') as f:
            csvr = csv.reader(f)
            csvr = list(csvr)
            for row in csvr:
                if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                    if edge_search_result_1 != 0 or edge_search_result_2 != 0:
                        if row[1].lstrip() == "switch":
                            # print("[i] Downstream Switch: {}, Status: {}, Availability: {}".format(row[0], row[4],
                            # row[13]))
                            down_switch_dict[row[0]] = row[4]
                        if row[1].lstrip() == "transformer":
                            pass
                            # print("[i] Downstream Transformer: {}, Status: {}, Availability: {}".format(row[0],
                            # row[4],
                            # row[13]))

        # except:
        #     print("[x] Error in downstream edge search.")

    return down_switch_dict


def edge_info(edgename):
    """

    :param edgename:
    :return:
    """
    return


def reconfigure(node_to_restore, damaged_graph, criteria="least_impact", filename=None):
    """
    Algorithm: Kruskal Minimum Spanning Tree
    Damaged graph.
    Path search from node_to_restore, in complete graph to generators
    :return:
    """

    generator_nodes = []
    complete_graph = gv.graph_collection[3]
    undir_complete_graph = nx.Graph()  # complete_graph.to_undirected()
    if filename is None:
        e_file = gv.filepaths["edges"]
    else:
        e_file = filename
    # Calculate the impact on edge and attribute it to undir_complete_graph:
    complete_graph_edgelist = complete_graph.edges()
    temp_edge_impact_dict = {}
    with open("edge_risk_profile_during_reconfiguration.csv", "w+", newline='') as risk_profile_data:
        for m in complete_graph_edgelist:
            edge_of_path_name_1 = m[0] + "_to_" + m[1]
            edge_of_path_name_2 = m[1] + "_to_" + m[0]
            edge_search_result_1 = db._edge_search(edge_of_path_name_1)
            edge_search_result_2 = db._edge_search(edge_of_path_name_2)
            with open(e_file, 'r+') as f:
                csvr = csv.reader(f)
                csvr = list(csvr)

                for row in csvr:
                    if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                        if edge_search_result_1 != 0:
                            impact = impact_on_edge(edge_of_path_name_1)
                            temp_edge_impact_dict[edge_of_path_name_1] = impact
                            undir_complete_graph.add_edge(m[0], m[1], weight=impact)
                            write_string = m[0] + "_to_" + m[1] + "," + str(impact) + "\n"
                            risk_profile_data.write(write_string)
                        elif edge_search_result_2 != 0:
                            impact = impact_on_edge(edge_of_path_name_2)
                            temp_edge_impact_dict[edge_of_path_name_1] = impact
                            undir_complete_graph.add_edge(m[1], m[0], weight=impact)
                            write_string = m[1] + "_to_" + m[0] + "," + str(impact) + "\n"
                            risk_profile_data.write(write_string)

    cn.add_node_attr(undir_complete_graph)
    for k, v in undir_complete_graph.nodes(data=True):
        if float(v['gen']) > 0 or v['gen'].lstrip() == "inf":
            generator_nodes.append(k)
    print("Available generator nodes are {}".format(generator_nodes))
    logging.info("Reconfiguration function called")
    logging.info("Available generator nodes are {}".format(generator_nodes))

    minimum_spanning_edges = nx.minimum_spanning_edges(undir_complete_graph, data=False)
    new_graph: DiGraph = nx.DiGraph()

    for m in minimum_spanning_edges:
        edge_of_path_name_1 = m[0] + "_to_" + m[1]
        edge_of_path_name_2 = m[1] + "_to_" + m[0]
        edge_search_result_1 = db._edge_search(edge_of_path_name_1)
        edge_search_result_2 = db._edge_search(edge_of_path_name_2)
        with open(e_file, 'r+') as f:
            csvr = csv.reader(f)
            csvr = list(csvr)

            for row in csvr:
                if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                    try:
                        impact = temp_edge_impact_dict[edge_of_path_name_1]
                    except:
                        impact = temp_edge_impact_dict[edge_of_path_name_2]

                    if edge_search_result_1 != 0:
                        new_graph.add_edge(m[0], m[1], weight=float(impact))

                    elif edge_search_result_2 != 0:
                        new_graph.add_edge(m[1], m[0], weight=float(impact))

    print("Edges in Restored Path:")
    print(new_graph.edges())

    g_new_edges = set(new_graph.edges())

    # Edge status comparison:
    g_old = gv.graph_collection[0]
    g_old_edges = set(g_old.edges())

    turn_on = g_new_edges.difference(g_old_edges)
    controllable_switches = {}
    for t in turn_on:
        edge_of_path_name_1 = t[0] + "_to_" + t[1]
        edge_of_path_name_2 = t[1] + "_to_" + t[0]
        edge_search_result_1 = db._edge_search(edge_of_path_name_1)
        edge_search_result_2 = db._edge_search(edge_of_path_name_2)
        try:
            with open(e_file, 'r+') as f:
                csvr = csv.reader(f)
                csvr = list(csvr)
                for row in csvr:
                    if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                        if edge_search_result_1 != 0 or edge_search_result_2 != 0:
                            edge_status_list[row[0]] = row[4]
                            if row[1].lstrip() == "switch":
                                # print("[i] Switch {} found!".format(row[0]))
                                controllable_switches[row[0]] = row[4]
        except:
            print("[x] Edge could not be queried for status for the nodes.")




    cn.add_node_attr(new_graph)
    cn.lat_long_layout(new_graph, show=True, save=False, title="Minimum Spanning Tree Restoration")

    try:
        cyclic_path = list(nx.find_cycle(new_graph, node_to_restore, orientation='ignore'))
        print(cyclic_path)
    except nx.NetworkXNoCycle:
        print("[i] All loads could be picked without loop elimination.")

    return controllable_switches


def restore(from_node, to_node, commit=False, control=False):
    """
    Change switch status is upstream and downstream edges.
    Run power flow to verify.

    Modeling Convention:
    If you are connecting it to a real-time device, such as RTDS, please remember that all switches are sorted
    alphabetically.

    """
    g2 = gv.graph_collection[1]
    edges = g2.edges()
    wg = nx.DiGraph()  # wg: working graph
    wg.add_edges_from(edges)
    try:
        down_switch_dict = downstream_edge_info(wg, from_node)
    except Exception as e:
        if KeyError:
            logging.info("From node was not found in the node file. May be a spelling error.")
            print("[x] 'From Node' was not correctly spelled when the 'reconfigure' function was called.")
            sys.exit()

    modified_down_switch_dict = {}
    up_switch_dict = upstream_edge_info(wg, from_node)
    print("Down switches from node:")
    pp.pprint(down_switch_dict)

    for k, v in down_switch_dict.items():
        mv = ''
        number_of_down_changes = 0
        number_of_up_changes = 0
        if v == '1' and number_of_down_changes == 0:
            modified_down_switch_dict[k] = mv

    print("Up switches from node:")
    pp.pprint(up_switch_dict)

    # edge_switches_reconfigured = {}
    # modified_v = ""
    # switching_operations = 0
    # for k, v in edge_switches:
    #     if v == "0":
    #         modified_v = "1"
    #         edge_switches_reconfigured[k] = mv
    #         switching_operations += 1
    #         print("[i] Switch {} needs to turned ON.")

    #         # search upstream switches, and turn them off.


def distant_between_two_points(p1, p2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    :return : Distance between two points in miles
    """
    lon1 = p1[0]
    lat1 = p1[1]

    lon2 = p2[0]
    lat2 = p2[1]

    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km/1.61


def primary_threat_anchor_of_node(node, ignore_multiple_threats_within="100"):
    """
    This method helps in finding out the threat nodes that will actually impact a certain node.
    :param node: instance of a node object
    :param ignore_multiple_threats_within: unit km, within this radius, multiple threat nodes are considered the same.
    :return: list of all threat anchors for the given node object, and assumed impact.
    """

    most_destructive_threat_anchor = ""
    strength = 1
    tmp_var = 100000  # <- any very large value
    proximal_threat_anchors = []  # <- todo: superposition impact of other threat nodes

    for k, value in gv.threat_dict.items():
        "Calculate distance between each threat node. "
        "Complexity: O(N^2)"  # <- todo: improve the runtime complexity

        distance = distant_between_two_points(tuple((float(value.lat), float(value.long))),
                                              tuple((float(node.lat), float(node.long))))

        if tmp_var > distance:
            most_destructive_threat_anchor = value.anchor
            strength = value.strength
            tmp_var = distance

        water_risk = value.water_risk
        fire_risk = value.fire_risk
        wind_risk = value.wind_risk
        seismic_risk = value.seismic_risk

    primary_threat_anchor = {"name": most_destructive_threat_anchor, "strength": strength, "distance": distance,
                             "water_risk": water_risk, "fire_risk": fire_risk, "wind_risk": wind_risk,
                             "seismic_risk": seismic_risk}
    logging.info("For node %s, the most significant threat anchor is %s" % (node.name, most_destructive_threat_anchor))

    return primary_threat_anchor


def primary_repair_base(node):
    """
    Primary repair base should be dependent on the type of event, and then sorted by distance from the node being
    studied.
    Suggested rules for choosing the primary repair base:
    - If the water risk is high at a particular node, the repair base with a lot of hand-pumps to extract out the water
    should be the primary repair base.
    - If wind risk is high, and node edges are connected by OH lines, a repair base with a lot of OH line, pole
    replacements, and crew_truck should be the primary reapir base.

    :param node:
    :return:
    """
    most_useful_repair_base = ""
    tmp_var = 100000  # <- any very large value
    repair_bases = {}

    repair_node_usefulness_score = 0

    for k, value in gv.repair_dict.items():
        "calculate distance between each threat node. "
        "Complexity: O(N^2)"  # <- todo: improve the runtime complexity

        distance = distant_between_two_points(tuple((float(value.lat), float(value.long))),
                                              tuple((float(node.lat), float(node.long))))

        threat_node = primary_threat_anchor_of_node(node)

        if float(threat_node["water_risk"]) > (float(node.water_cc) / 10.0) * float(settings["tolerances"][node.category.lstrip()]["water"]) and float(value.handpump) > 0:
            repair_node_usefulness_score += float(value.handpump)

        if float(threat_node["wind_risk"]) > (float(node.wind_cc) / 10.0) * float(settings["tolerances"][node.category.lstrip()]["wind"]) and float(value.line) > 0 and float(value.pole) > 0:
            repair_node_usefulness_score += (float(value.line) + float(value.pole) + float(value.switches) + float(value.mobile_genset))

        if float(threat_node["fire_risk"]) > (float(node.fire_cc) / 10.0) * float(settings["tolerances"][node.category.lstrip()]["fire"]) and float(value.transformer) > 0 and float(value.pole) > 0:
            repair_node_usefulness_score += (float(value.line) + float(value.transformer) + float(value.pole) + float(value.switches) + float(value.mobile_genset))

        if float(threat_node["seismic_risk"]) > (float(node.seismic_cc) / 10.0) * float(settings["tolerances"][node.category.lstrip()]["seismic"]) and float(value.mobile_genset) > 0 and float(value.pole) > 0 and float(value.line) > 0:
            repair_node_usefulness_score = (float(value.handpump) + float(value.line) + float(value.transformer) + float(value.pole) + float(value.switches) + float(value.mobile_genset))

        repair_bases[k] = repair_node_usefulness_score

    most_useful_repair_base = max(repair_bases.keys(), key=(lambda key: repair_bases[key]))
    max_usefulness_score = repair_bases[most_useful_repair_base]

    for kk, vv in repair_bases.items():
        repair_bases[kk] = vv/max_usefulness_score

    # Normalization to ensure all usefulness scores are reported at values less than or equal to 1
    most_useful_repair_base = max(repair_bases.keys(), key=(lambda key: repair_bases[key]))

    primary_repair_base = {"name": most_useful_repair_base, "distance": distance, "repair_bases": repair_bases}
    logging.info("For node %s, the most useful repair base is %s" % (node.name, primary_repair_base['name']))

    return primary_repair_base


def node_repairability(n):
    """
    This function helps calculate how easy is it for repair crew to navigate to damaged sites, and have accessibility
    to resources to quickly repair the damages.
    :param n:
    :return:
    """
    node = node_object_from_node_name(n)
    prb = primary_repair_base(node)
    inc = interdependent_network_connectivity()
    x = prb["distance"] * inc["transport"] * 1/np.exp(event_intensity(n))

    return x


def impact_on_nodes(obj_nodes):
    """

    :param obj_nodes:
    :return: Dictionary that has all node names and corresponding impact of an event on that node.
    """
    for n in obj_nodes:
        gv.node_risk_dict[n.name] = float(impact_on_node(n))

    return gv.node_risk_dict


def impact_on_node(node_name):
    """
    impact = (strength of event/distance from threat node)*risk of the node
    :return:
    """

    node_name = node_name.lstrip()
    node = node_object_from_node_name(node_name)

    threat_anchor = primary_threat_anchor_of_node(node)

    logging.info('Calculating impact of threat labeled %s on node %s' % (threat_anchor["name"], node.name))

    # DEFAULTS
    # ---------
    water_tolerance = settings["tolerances"][node.category.lstrip()]["water"]  # FT
    wind_tolerance = settings["tolerances"][node.category.lstrip()]["wind"]
    fire_tolerance = settings["tolerances"][node.category.lstrip()]["fire"]
    seismic_tolerance = settings["tolerances"][node.category.lstrip()]["seismic"]

    if node.category.lstrip() == "res":
        try:
            relative_importance = gv.node_res[node.name]
        except:
            relative_importance = 2
    elif node.category.lstrip() == "biz":
        try:
            relative_importance = gv.node_biz[node.name]
        except:
            relative_importance = 4
    elif node.category.lstrip() == "wlf":
        try:
            relative_importance = gv.node_wlf[node.name]
        except:
            relative_importance = 8
    elif node.category.lstrip() == "shl":
        try:
            relative_importance = gv.node_shl[node.name]
        except:
            relative_importance = 9
    elif node.category.lstrip() == "law":
        try:
            relative_importance = gv.node_law[node.name]
        except:
            relative_importance = 4
    elif node.category.lstrip() == "wat":
        try:
            relative_importance = gv.node_wat[node.name]
        except:
            relative_importance = 6
    elif node.category.lstrip() == "com":
        try:
            relative_importance = gv.node_com[node.name]
        except KeyError:
            relative_importance = 1
    elif node.category.lstrip() == "trn":
        try:
            relative_importance = gv.node_trn[node.name]
        except:
            relative_importance = 6
    elif node.category.lstrip() == "sup":
        try:
            relative_importance = gv.node_sup[node.name]
        except:
            relative_importance = 7
    else:
        try:
            relative_importance = gv.node_utl[node.name]
        except:
            relative_importance = 9

    # WATER

    water_risk_escalation = 1
    anticipated_water_risk = float(threat_anchor["water_risk"])
    if anticipated_water_risk > 0.95 * float(water_tolerance):
        water_risk_escalation = (anticipated_water_risk - 0.95 * float(water_tolerance)) * 0.1
    overall_water_risk = water_risk_escalation * (anticipated_water_risk / water_risk_escalation)
    if node.preexisting_damage.lstrip() == "1":
        overall_water_risk = overall_water_risk * 1.25

    # WIND

    wind_risk_escalation = 1
    anticipated_wind_risk = float(threat_anchor["wind_risk"])
    if anticipated_wind_risk > 0.90 * float(wind_tolerance):
        wind_risk_escalation = (anticipated_wind_risk - 0.90 * float(wind_tolerance)) * 0.1
    overall_wind_risk = wind_risk_escalation * (anticipated_water_risk / water_risk_escalation)
    if node.preexisting_damage.lstrip() == "1":
        overall_wind_risk = overall_wind_risk * 1.25

    # FIRE

    fire_risk_escalation = 1
    anticipated_fire_risk = float(threat_anchor["fire_risk"])
    if anticipated_fire_risk > 0.98 * float(fire_tolerance):
        fire_risk_escalation = (anticipated_fire_risk - 0.98 * float(fire_tolerance)) * 0.1
    overall_fire_risk = fire_risk_escalation * (anticipated_water_risk / water_risk_escalation)
    if node.preexisting_damage.lstrip() == "1":
        overall_fire_risk = overall_fire_risk * 2.0

    # SEISMIC

    seismic_risk_escalation = 1
    anticipated_seismic_risk = float(threat_anchor["seismic_risk"])
    if anticipated_seismic_risk > 0.90 * float(seismic_tolerance):
        seismic_risk_escalation = (anticipated_water_risk - 0.95 * float(seismic_tolerance)) * 0.1
    overall_seismic_risk = seismic_risk_escalation * (anticipated_water_risk / water_risk_escalation)
    if node.preexisting_damage.lstrip() == "1":
        overall_seismic_risk = overall_seismic_risk * 2.5

    total_risk = (relative_importance * float(node.foliage) * (
            overall_wind_risk / float(node.wind_cc) + overall_water_risk / float(
        node.water_cc) + overall_fire_risk / float(node.fire_cc) + overall_seismic_risk / float(node.seismic_cc))) / (
                     float(threat_anchor['distance']))

    return total_risk


def node_resiliency(n, verbose=False):
    """
    Ability to withstand an impact, and recover in multiple ways.
    :return:
    """
    node = node_object_from_node_name(n)
    graph = gv.graph_collection[1]
    graph = graph.to_undirected()
    generator_nodes = []
    path_counter = 0
    for k, v in graph.nodes(data=True):
        try:
            if float(v['gen']) > 0 or v['gen'].lstrip() == "inf":
                generator_nodes.append(k)
        except:
            continue
    # print("[i] Available generator nodes that can be used to restore {} are {}".format(n, generator_nodes))
    for g in generator_nodes:
        path = nx.all_simple_paths(graph, n, g)
        path_counter += len(list(path))

    node_res = path_counter

    if float(node.backup_dg.lstrip()) > 0.01:
        node_res += float(node.backup_dg.lstrip())

    threat_anchor = primary_threat_anchor_of_node(node)

    if float(threat_anchor["wind_risk"]) > 75:
        node_res = 0
        # if node_res != 0:
        #     node_res = node_res * float(node.wind_cc.lstrip()) / 10.0
        # else:
        #     node_res = float(node.wind_cc.lstrip()) / 10.0

    if float(threat_anchor["water_risk"]) > 2.0:
        node_res = 0
        if node_res != 0:
            node_res = node_res * float(node.water_cc.lstrip()) / 10.0
        else:
            node_res = float(node.water_cc.lstrip()) / 10.0

    if float(threat_anchor["seismic_risk"]) > 5:
        node_res = 0
        # if node_res != 0:
        #     node_res = node_res * float(node.seismic_cc.lstrip()) / 10.0
        # else:
        #     node_res = float(node.seismic_cc.lstrip()) / 10.0

    if float(threat_anchor["fire_risk"]) > 150:
        node_res = 0
        # if node_res != 0:
        #     node_res = node_res * float(node.fire_cc.lstrip()) / 10.0
        # else:
        #     node_res = float(node.fire_cc.lstrip()) / 10.0

    if verbose:
        print("-------------------------")
        print("Node name    : {}".format(n))
        print("Redundancy   : {}".format(path_counter))
        print("Backup       : {}".format(node.backup_dg.lstrip()))
        print("Fire Proof   : {}".format(node.fire_cc.lstrip()))
        print("Water Proof  : {}".format(node.water_cc.lstrip()))
        print("Wind Proof   : {}".format(node.wind_cc.lstrip()))
        print("Seimic Tol.  : {}".format(node.seismic_cc.lstrip()))
        print("--------------------------")
        print("RESILIENCY   : {}".format(node_res))
        print("--------------------------\n")

    return node_res


def path_search(G, n1, n2, criterion="least_risk"):
    """

    :param G: Graph object
    :param n1: source node in a graph object
    :param n2: sink node in a graph object
    :return: path:
    """
    if criterion == "least_risk":
        path = nx.dijkstra_path(G, n1, n2, 'impact_on_edge')
    load_and_demand_query(path)
    return path


def find_spanning_tree():
    """
    Cover maximum nodes in a damaged network, using least number of edges, or such that the lowest sum of edges are achieved.
    Implementation of Kruskal's Algorithm.
    Validated.
    :return:
    """

    pass


def load_and_demand_query(path, verbose=True):
    loads = 0
    gens = 0
    demand_kw = 0.0
    gen_kw = 0.0
    e_file = gv.filepaths["edges"]
    if type(path) is str:
        n = node_object_from_node_name(path)
    else:
        for p in path:
            n = node_object_from_node_name(p)
            i = path.index(p)
            if i < len(path) - 1:
                q = path[i + 1]
                edge_of_path_name_1 = p + "_to_" + q
                edge_of_path_name_2 = q + "_to_" + p
                edge_search_result_1 = db._edge_search(edge_of_path_name_1)
                edge_search_result_2 = db._edge_search(edge_of_path_name_2)
                try:
                    with open(e_file, 'r+') as f:
                        csvr = csv.reader(f)
                        csvr = list(csvr)
                        for row in csvr:
                            if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                                if edge_search_result_1 != 0 or edge_search_result_2 != 0:
                                    edge_status_list[row[0]] = row[4]
                                    if row[1].lstrip() == "switch":
                                        # print("[i] Switch {} found!".format(row[0]))
                                        edge_switches[row[0]] = row[4]
                except:
                    print("[x] Edge could not be queried for status for the nodes.")

            if int(n.load) > 0:
                loads += 1
                demand_kw += float(n.load)
            if n.gen.lstrip() != "inf":
                gen_kw += float(n.gen)

    if verbose:
        print("[i] Number of loads = {}, Demand = {} kW, Generation = {} kW".format(loads, demand_kw, gen_kw))
        print("[i] Edge Statuses of the path:")
        pp.pprint(edge_status_list)

        if verbose:
            print("[i] Switch Status:")
            pp.pprint(edge_switches)

    load_and_demand_query_dict = {}
    load_and_demand_query_dict["edge_status"] = edge_status_list
    load_and_demand_query_dict["switch_status"] = edge_switches

    return load_and_demand_query_dict


def adjusted_node_risk(node_risk, adjustment_factor):
    """
    :param node_risk:
    :param new_information:
    :return:
    """
    return node_risk * adjustment_factor


def node_threat(n_risk, cta, threat_type="Generic", threat_horizon="day", threat_credibility="1"):
    """
    This function calculates the threat at each node
    :param threat_horizon: options: day (default, hour, two_day, week, two_week, month, few-months, year)
    :param threat_credibility: min: 0, max: 1 (default).
    :param n_risk:
    :param threat_type: default value is Generic, other possible values can be based on event.
    :param cta: closest_threat_anchor: A tuple containing lat, long of a threat anchor
    :return: node_threat_value
    """
    node_threat_value = 0
    return node_threat_value


def node_risk_estimator(n, overall_bias=1):
    """
    Risk Formula = max_risk - (wind_risk_factor*Wind_CC +
                               water_risk_factor*Water_CC +
                               fire_risk_factor*Fire_CC +
                               eq_risk_factor*Seismic_CC)/40

    where, CC = Code Conformity
    :param n: Row from the CSV file that has all the information about the node
    :param overall_bias: additional control variable to customize the description of impact of an event on a node.
           For example, for all hospitals might be at lower risk due to last minute efforts,
            we can say overall_bias < 1, e.g. 0.4, but typically n[15] and overall_bias values are kept at 1
    :return: risk of a node, based on its location and conformity to construction standards
             1 means maximum risk, 0 means minimum risk.
             Lower value is clearly better.
    """
    # return 0.24

    return 1 - overall_bias * float(n[15].lstrip()) * (float(gv.event["wind_risk"]) * float(n[11].lstrip()) +
                                                       float(gv.event["water_risk"]) * float(n[12].lstrip()) +
                                                       float(gv.event["fire_risk"]) * float(n[14].lstrip()) +
                                                       float(gv.event["seismic_risk"]) * float(n[13].lstrip())) / 40.0


def impact_on_edges():
    pass


def event_intensity(node_name):
    """

    :return: event_intensity
    """

    node = node_object_from_node_name(node_name)
    threat_node = primary_threat_anchor_of_node(node)

    wind_event_intensity = 4
    fire_event_intensity = 1
    seismic_event_intensity = 2
    water_event_intensity = 2

    if float(threat_node["wind_risk"]) > 75 and float(threat_node["wind_risk"]) < 100:
        wind_event_intensity = 6
    elif float(threat_node["wind_risk"]) >= 100 and float(threat_node["wind_risk"]) < 120:
        wind_event_intensity = 8
    elif float(threat_node["wind_risk"]) >= 120:
        wind_event_intensity = 10

    if float(threat_node["fire_risk"]) > 150 and float(threat_node["fire_risk"]) < 200 and float(threat_node["duration"]) >= 1:
        fire_event_intensity = 6
    elif float(threat_node["fire_risk"]) > 150 and float(threat_node["fire_risk"]) < 200 and float(threat_node["duration"]) >= 2:
        fire_event_intensity = 8
    elif float(threat_node["fire_risk"]) > 200 and float(threat_node["duration"]) >= 2:
        fire_event_intensity = 10

    if float(threat_node["seismic_risk"]) >= 5 and float(threat_node["seismic_risk"]) < 6:
        seismic_event_intensity = 6
    elif float(threat_node["seismic_risk"]) >= 6 and float(threat_node["seismic_risk"]) < 7.5:
        seismic_event_intensity = 8
    elif float(threat_node["seismic_risk"]) >= 7.5:
        seismic_event_intensity = 10

    if float(threat_node["water_risk"]) > 2 and float(threat_node["water_risk"]) < 5:
        water_event_intensity = 6
    elif float(threat_node["water_risk"]) >= 5 and float(threat_node["water_risk"]) < 8:
        water_event_intensity = 8
    elif float(threat_node["water_risk"]) >= 8:
        water_event_intensity = 10

    ei = 0.25 * (wind_event_intensity+fire_event_intensity+seismic_event_intensity+water_event_intensity)

    return ei


def edge_object_from_edge_name(e_name):
    edge_names = [e.name for e in gv.obj_edges]
    if e_name in edge_names:
        i = edge_names.index(e_name)
        return gv.obj_edges[i]
    else:
        print("[x] %s could not be found or created as an edge object. Check your edge database, i.e. edge-file.csv or "
              "something similar." % e_name)
        return False


def impact_on_edge(e):
    """
    Risk = (foliage_risk*elemental_risk*event_intensity*max(risk_of_from_node, risk_of_to_node))/hardening
    :param e: Key of edge dictionary for global edge risk dictionary
    :return:
    """
    edge_name = e  # e[1].lstrip() + "_to_" + e[0].lstrip()
    edge = edge_object_from_edge_name(edge_name)
    elemental_risk = (float(edge.wind_risk) + float(edge.fire_risk) + float(edge.water_risk)) / 30.0
    foliage_risk = 1.0  # <-- todo: need to implement the foliage risk factor
    # where's the closest threat node?
    e_file = gv.filepaths["edges"]
    edge_search_result = db._edge_search(edge_name)
    hardening = 1
    try:
        with open(e_file, 'r+') as f:
            csvr = csv.reader(f)
            csvr = list(csvr)
            for row in csvr:
                if row[0].lstrip() == edge_name and edge_search_result != 0:
                    from_node_of_e = row[2].lstrip()
                    to_node_of_e = row[3].lstrip()
                    hardening = float(row[12])
    except:
        print("[x] Cannot find the requested edge.\n[i] Calculating impact on substation PCC instead.")
        from_node_of_e = "S1"
        to_node_of_e = "F1_1"
        return

    ev_intensity_from = float(event_intensity(from_node_of_e))
    ev_intensity_to = float(event_intensity(to_node_of_e))
    ev_intensity = 0.5 * (ev_intensity_from + ev_intensity_to)
    # primary_threat_anchor = primary_threat_anchor_of_node(from_node_of_e)
    risk_of_from_node = impact_on_node(from_node_of_e)
    risk_of_to_node = impact_on_node(to_node_of_e)
    x = (foliage_risk * ev_intensity * max(risk_of_from_node, risk_of_to_node)) / hardening
    return x


def nodal_calculations(graph, visualize=True, title=""):

    print(graph.nodes())
    print(graph.edges())
    nodes = graph.nodes()
    sort_node_by_type()

    project_config_file = open(gv.filepaths["model"])
    project_settings = json.load(project_config_file)
    project_config_file.close()
    logging.info("Performing node risk calculation for all nodes")
    file_name = "nodal_calculation.csv"

    with open(file_name, 'w+') as node_file:
        node_file.write('name,lat,long,risk,resiliency,repairability\n')
        for k, v in nodes.items():
            x = impact_on_node(k.lstrip())
            y = node_resiliency(k.lstrip())
            z = node_repairability(k.lstrip())
            write_string = k + "," + v['lat'].lstrip() + "," + v['long'].lstrip() + "," + str(x) + "," + str(y) + "," + str(z) +"\n"
            node_file.write(write_string)


def node_object_from_node_name(n_name):
    """

    :param n_name:
    :return:
    """
    node_names = [n.name for n in gv.obj_nodes]
    if n_name in node_names:
        i = node_names.index(n_name)
        return gv.obj_nodes[i]
    else:
        print("[x] %s could not be found or created as a node object. Check your database." % n_name)
        return False


def sort_node_by_type():
    """
    Types of node: res = residential,
                   biz = business,
                   wlf = welfare,
                   shl = shelter,
                   law = law enforcement,
                   wat = water utility,
                   com = communication,
                   trn = transportation,
                   sup = supply chain,
                   src = generation node
                   sub = substation node, swing bus for the feeder
    :param type:
    :return:
    """
    node_file = gv.project["data"]["nodes"]

    with open(node_file) as f:
        has_header = csv.Sniffer().has_header(f.read(1024))
        f.seek(0)
        nodes = csv.reader(f)
        if has_header:
            next(nodes)  # Skip header row

        for node in nodes:
            if node[9].lstrip() == "res":
                gv.node_res[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "biz":
                gv.node_biz[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "wlf":
                gv.node_wlf[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "shl":
                gv.node_shl[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "law":
                gv.node_law[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "wat":
                gv.node_wat[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "com":
                gv.node_com[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "trn":
                gv.node_trn[node[0]] = node_risk_estimator(node)
            elif node[9].lstrip() == "sup":
                gv.node_sup[node[0]] = node_risk_estimator(node)
            else:
                gv.node_utl[node[0]] = node_risk_estimator(node)


def resiliency_downstream(graph, edgelist, event):
    """
    This function computes the resiliency of all downstream sections,
    mainly looking out for critical loads
    :param graph:
    :param edgelist: All downstream sections of the feeder, from perspective of an edge being analyzed
    :param event: dictionary describing the event magnitude
    :return:
    """
    print(edgelist)

    for e in edgelist:
        for oe in gv.obj_edges:
            if e[0].lstrip() == oe.from_node.lstrip() and e[1].lstrip() == oe.to_node.lstrip():
                gv.edge_risk_dict[tuple((e[0], e[1]))] = (event["water_risk"] * float(oe.water_risk.lstrip())
                                                          + event["wind_risk"] * float(oe.wind_risk.lstrip())
                                                          + event["fire_risk"] * float(oe.fire_risk.lstrip())) / 30

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


def weigh_the_sections(graph, attr_name="impact_on_edge"):
    edgelist = graph.edges()
    for e in edgelist:
        edge_name = e[0].lstrip() + "_to_" + e[1].lstrip()
        x = impact_on_edge(edge_name)
        graph[e[0]][e[1]][attr_name] = x
        # print("[i] Weighing {} by anticipated event impact {}".format(edge_name, x))


def resiliency_2(analysis='nodal'):
    """
    This function helps compute the resiliency metric of the network of a
    node, or a network
    :param kwargs:
    :return:
    """

    # 0. what's the event?
    event = {"water_risk": 0.9, "wind_risk": 1.2, "fire_risk": 0.8}

    # 1. get the graphs

    g1 = gv.graph_collection[0]
    g2 = gv.graph_collection[1]
    nodes = g1.nodes()
    edges = g1.edges()
    print(nodes)
    print(edges)

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
