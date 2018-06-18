from pycanvass.all import *
import networkx as nx

project, nodes, edges = load_project()

network = build_network(nodes,edges)
mygraph = network["normal"]
# threat_graph()
node_risk_calculation(mygraph, title="Tropical Storm: Wind Speeds upto 97 mph, 10 ft water logging")
# mygraph2 = lose_edge('F1_3', 'F1_4')
# print(type(mygraph2))
# print(type(mygraph2))
# reconfigure('F1_4',mygraph2)

# node_risk_calculation(mygraph)
# layout_model("C:\\Users\\Sayon\\Documents\\CANVASS\\Example_Project\\edge-file.csv")

# get_data("rtds",8989,1)