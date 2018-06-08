import pycanvass.global_variables as gv
import networkx as nx
import csv
import random
import numpy as np
import pycanvass.data_bridge as db
import pprint

pp = pprint.PrettyPrinter(indent=4)

global edge_status_list
edge_status_list = {}

global edge_switches
edge_switches = {}

def upstream_edge_info(wg, n):
    upstream_edges = list(nx.edge_dfs(wg, n, orientation='reverse'))
    print(upstream_edges)
    up_switch_dict = {}
    e_file = gv.filepaths["edges"]
    for u in upstream_edges:
        # edge info:
        p = u[0].lstrip()
        q = u[1].lstrip()
        edge_of_path_name_1 = p + "_to_" + q
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
                                print("[i] Upstream Switch: {}, Status: {}, Availability: {}".format(row[0], row[4], row[13]))
                                up_switch_dict[row[0]] = row[4]
                            if row[1].lstrip() == "transformer":
                                print("[i] Upstream Transformer: {}, Status: {}, Availability: {}".format(row[0], row[4], row[13]))
                                
        except:
            print("[x] Error in up-stream edge search.")
    return up_switch_dict

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
        try:
            with open(e_file, 'r+') as f:
                csvr = csv.reader(f)
                csvr = list(csvr)
                for row in csvr:
                    if row[0].lstrip() == edge_of_path_name_1 or row[0].lstrip() == edge_of_path_name_2:
                        if edge_search_result_1 != 0 or edge_search_result_2 != 0:
                            if row[1].lstrip() == "switch":
                                print("[i] Downstream Switch: {}, Status: {}, Availability: {}".format(row[0], row[4], row[13]))
                                down_switch_dict[row[0]] = row[4]
                            if row[1].lstrip() == "transformer":
                                print("[i] Downstream Transformer: {}, Status: {}, Availability: {}".format(row[0], row[4], row[13]))
                                
        except:
            print("[x] Error in downstream edge search.")
            
    return down_switch_dict

def edge_info(edgename):
    return


def reconfigure(from_node, to_node, commit=False, control=False):
    """
    Change switch status is upstream and downstream edges.
    Run power flow to verify. 
    """
    g2 = gv.graph_collection[1]
    edges = g2.edges()
    wg = nx.DiGraph()  # wg: working graph
    wg.add_edges_from(edges)
    down_switch_dict = downstream_edge_info(wg, from_node)
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
    return km


def primary_threat_anchor_of_node(node, ignore_multiple_threats_within="100"):
    """
    This method helps in finding out the threat nodes that will actually impact a certain node.
    :param node: instance of a node object
    :param ignore_multiple_threats_within: unit km, within this radius, multiple threat nodes are considered the same.
    :return: list of all threat anchors for the given node object, and assumed impact.
    """

    most_destructive_threat_anchor = ""
    strength = 1
    tmp_var = 100000                # <- any very large value
    proximal_threat_anchors = []    # <- todo: superposition impact of other threat nodes

    for k, value in gv.threat_dict.items():
        "calculate distance between each threat node. "
        "Complexity: O(N^2)"        # <- todo: improve the runtime complexity

        distance = distant_between_two_points(tuple((float(value.lat), float(value.long))),
                                       tuple((float(node.lat), float(node.long))))

        if tmp_var > distance:
            most_destructive_threat_anchor = value.anchor
            strength = value.strength
            tmp_var = distance

    primary_threat_anchor = {"name": most_destructive_threat_anchor, "strength": strength, "distance": distance}
    # print("For node %s, the most significant threat anchor is %s" % (node.name ,most_destructive_threat_anchor))

    return primary_threat_anchor


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
    node_name=node_name.lstrip()
    node = node_object_from_node_name(node_name)
    
    threat_anchor = primary_threat_anchor_of_node(node)

    print('Calculating impact of threat labeled %s on node %s' % (threat_anchor["name"], node.name))
    risk = 1
    if node.category.lstrip() == "res":
        risk = gv.node_res[node.name]
    elif node.category.lstrip() == "biz":
        risk = gv.node_biz[node.name]
    elif node.category.lstrip() == "wlf":
        risk = gv.node_wlf[node.name]
    elif node.category.lstrip() == "shl":
        risk = gv.node_shl[node.name]
    elif node.category.lstrip() == "law":
        risk = gv.node_law[node.name]
    elif node.category.lstrip() == "wat":
        risk = gv.node_wat[node.name]
    elif node.category.lstrip() == "com":
        risk = gv.node_com[node.name]
    elif node.category.lstrip() == "trn":
        risk = gv.node_trn[node.name]
    elif node.category.lstrip() == "sup":
        risk = gv.node_sup[node.name]
    else:
        risk = gv.node_utl[node.name]

    return (float(threat_anchor["strength"])/float(threat_anchor["distance"]))*risk


def path_search(G, n1, n2, criterion="least_risk"):
    """

    :param G: Graph object
    :param n1: source node in a graph object
    :param n2: sink node in a graph object
    :return: path:
    """
    if criterion=="least_risk":
        path = nx.dijkstra_path(G, n1, n2, 'impact_on_edge')
    load_and_demand_query(path)
    return path



def load_and_demand_query(path):
    loads = 0
    gens = 0
    demand_kw = 0.0
    gen_kw = 0.0
    e_file = gv.filepaths["edges"]
    
    for p in path:
        n = node_object_from_node_name(p)
        i = path.index(p)
        if i < len(path)-1:
            q = path[i+1]
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
                                    print("[i] Switch {} found!".format(row[0]))
                                    edge_switches[row[0]] = row[4]
            except:
                print("[x] Edge could not be queried for status for the nodes.")
                
        if int(n.load) > 0:
            loads += 1
            demand_kw += float(n.load)
        if n.gen.lstrip() != "inf":
            gen_kw += float(n.gen)


    print("[i] Number of loads = {}, Demand = {} kW, Generation = {} kW".format(loads, demand_kw, gen_kw))
    print("[i] Edge Statuses of the path:")
    pp.pprint(edge_status_list)
    
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
    return node_risk*adjustment_factor


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
    return 1 - overall_bias * float(n[15].lstrip()) * (gv.event["wind_risk"] * float(n[11].lstrip()) +
                                                       gv.event["water_risk"] * float(n[12].lstrip()) +
                                                       gv.event["fire_risk"] * float(n[14].lstrip()) +
                                                       gv.event["seismic_risk"] * float(n[13].lstrip())) / 40.0


def impact_on_edges():
    pass


def event_intensity():
    """

    :return: event_intensity
    """
    event_intensity_number = gv.project["event"]["known_intensity"]
    if gv.project["event"]["type"] == "hurricane":
        event_intensity_number = event_intensity_number*2       # because worst hurricane value is 5
    return event_intensity_number                               # on a scale of 1 to 10, like earthquake scale.


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
    edge_name = e #e[1].lstrip() + "_to_" + e[0].lstrip()
    edge = edge_object_from_edge_name(edge_name)
    elemental_risk = (float(edge.wind_risk) + float(edge.fire_risk) + float(edge.water_risk))/30.0
    foliage_risk = 1.0            # <-- todo: need to implement the foliage risk factor
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
                    from_node_of_e = row[2]
                    to_node_of_e = row[3]
                    hardening = float(row[12])
    except:
        print("[x] Cannot find the requested edge.\n[i] Calculating impact on substation PCC instead.")
        from_node_of_e = "S1"
        to_node_of_e = "F1_1"
        return 

    ev_intensity = float(event_intensity())
    # primary_threat_anchor = primary_threat_anchor_of_node(from_node_of_e)
    risk_of_from_node = impact_on_node(from_node_of_e)
    risk_of_to_node = impact_on_node(to_node_of_e)
    x = (foliage_risk*ev_intensity*max(risk_of_from_node, risk_of_to_node))/hardening
    return x


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




def resiliency(analysis='nodal'):
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

