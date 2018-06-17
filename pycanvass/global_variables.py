"""
This file contains all the frequently used global variables
used by other parts of the program

author: Sayonsom Chanda
version: 0.0.4
package: PyCanvass
last_modified: 05/16/2018

"""

global filepaths
filepaths = {'nodes': "", 'edge': "", 'model': "", 'metric': "", "backup": {'nodes': "", 'edge': ""}}

global data_from_device
data_from_device = {}

global event
event = {"water_risk": 0.069, "wind_risk": 0.1, "fire_risk": 1, "seismic_risk" : 1.0}

global node_risk_dict
node_risk_dict = {}

global edge_risk_dict
edge_risk_dict = {}

global wind_risk_values
wind_risk_values = []

global water_risk_values
water_risk_values = []

global fire_risk_values
fire_risk_values = []

global cyber_risk_values
cyber_risk_values = []

global obj_nodes
obj_nodes = []

global obj_edges
obj_edges = []

global project
project = {}

global open_edges_list
open_edges_list = []

global closed_edges_list
closed_edges_list = []

global threat_dict
threat_dict = {}

global all_sources
all_sources = {}

global all_loads
all_loads = {}

global all_critical_loads
all_critical_loads = {}

global graph_collection
graph_collection = []

global node_res
node_res = {}

global node_biz
node_biz = {}

global node_law
node_law = {}

global node_shl
node_shl = {}

global node_sup
node_sup = {}

global node_wat
node_wat = {}

global node_com
node_com = {}

global node_trn
node_trn = {}

global node_wlf
node_wlf = {}

global node_utl
node_utl = {}

