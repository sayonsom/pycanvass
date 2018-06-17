import pycanvass.utilities as util

import sys
import time

demand_rt = sys.argv[1].replace(',','')
demand_rt = demand_rt.lstrip()
demand_rt = demand_rt.replace('(','').replace(')','')

gen_rt = sys.argv[2].replace(',','')
demand_rt = gen_rt.lstrip()
demand_rt = gen_rt.replace('(','').replace(')','')

for arg, in sys.argv:
    util.clean_data(arg)




def later_metric(graph, node_file, demand_rt, demand_now, t_event):
    """
    This metric was developed as a part of GMLC 1_3_9 project.
    :param graph:
    :param node_file:
    :param demand_rt:
    :param demand_now:
    :param t_event:
    :return:
    """

    n_file = gv.filepaths["nodes"]
    all_nodes = graph.nodes()
    all_node_metrics = {}
    for n in all_nodes:
        node_search_result = _node_search(n)

        try:
            with open(n_file, 'r') as f:
                csvr = csv.reader(f)
                csvr = list(csvr)
                for row in csvr:
                    if row[0].lstrip() == n:
                        if node_search_result is not 0:
                            demand_pre = graph.node[n]['demand'] = row[5].lstrip()
                            t_now = time.time()
                            metric = (row[8] * demand_now / demand_pre) / (t_now - t_event)
                            all_node_metrics[n] = metric
        except:
            print("Error, bye bye")
            sys.exit()

    return all_node_metrics
