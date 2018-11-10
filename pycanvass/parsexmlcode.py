from bs4 import BeautifulSoup
import csv
import networkx as nx
import matplotlib.pyplot as plt
import random

path = 'edgelist.csv'
allfroms = []
alltos = []
allnodes = []

def calculate_real_value(fakecount):
	return (fakecount-3)/2

def write_to_edge_csv(data, path):
    with open(path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)

def add_to_forms_and_tos(froms, tos):
	for f in froms:
		allfroms.append(f.contents[0])

	for t in tos:
		alltos.append(t.contents[0])

def node_processing(nameofnode):
	for n in nameofnode:
		allnodes.append(n.contents[0])

def meter_processing(meters, n_meters):
    meter_counter = 0
    
    if (n_meters != 0):
        mdf = open("meter_data.json","w+")
        mdfcsv = open("meter_data.csv", "w+")
        mdf.write("{\"data\":\n\t[")
    else:
        return;
    for m in meters:
        if (m.find('measured_real_energy') != -1 and m.find('measured_real_energy') != None):
            meter_counter += 1
            meter_name = m.find('name').contents[0]
            real_energy = m.find('measured_real_energy').contents[0]
            status = m.find('service_status').contents[0]
            real_power = m.find('measured_power').contents[0]
            #print(meter_name,real_energy,status,real_power)
            #% meter_name, real_energy, real_power, status, "127.0.0.1", "4575"
            randomportnumber = random.randint(2000,8000)
            if (meter_counter<n_meters):
                mdf.write(f"\n\t\t[\"{meter_name}\",\"{real_energy}\",\"{real_power}\",\"{status}\",\"127.0.0.1\",\"{randomportnumber}\"],")
                mdfcsv.write(f"{meter_name},{real_energy},{real_power},{status},127.0.0.1,{randomportnumber}\n")
            elif (meter_counter==n_meters):
                mdf.write(f"\n\t\t[\"{meter_name}\",\"{real_energy}\",\"{real_power}\",\"{status}\",\"127.0.0.1\",\"{randomportnumber}\"]\n\t]")
                mdfcsv.write(f"{meter_name},{real_energy},{real_power},{status},127.0.0.1,{randomportnumber}\n")
                mdf.write("}")

    mdf.close()
    mdfcsv.close()



with open("test.xml") as fp:
    soup = BeautifulSoup(fp,'lxml')
    y = BeautifulSoup(str(soup), 'lxml')

    

    # NODES
    poles = soup.gridlabd.powerflow.node_list
    print("finding poles")
    nameofnode = poles.findAll('name')
    
    # nodephases = poles.findAll('phases')
    # nodebustype = poles.findAll('bustype')
    # nodebusvoltage = poles.findAll('nominal_voltage')
    print("finding poles")
    node_processing(nameofnode)

    #print(poles)

    loads = soup.gridlabd.powerflow.load_list
    nameofnode = loads.findAll('name')
    # loads must have a parent meter, so the meter node will be considered as the load node
    # node_processing(nameofnode)

    motors = soup.gridlabd.powerflow.motor_list
    nameofnode = motors.findAll('name')
    print("finding motors")
    node_processing(nameofnode)

    capacitors = soup.gridlabd.powerflow.capacitor_list
    nameofnode = capacitors.findAll('name')
    print("finding motors")
    node_processing(nameofnode)

    substations = soup.gridlabd.powerflow.substation_list
    nameofnode = substations.findAll('name')
    print("finding motors")
    node_processing(nameofnode)

    meters = soup.gridlabd.powerflow.meter_list
    nameofnode = meters.findAll('name')
    print("finding motors")
    print(nameofnode)
    node_processing(nameofnode)
    

    triplex_meters = soup.gridlabd.powerflow.triplex_meter_list
    nameofnode = triplex_meters.findAll('name')
    node_processing(nameofnode)

    triplex_loads = soup.gridlabd.powerflow.triplex_load_list
    nameofnode = triplex_loads.findAll('name')
    node_processing(nameofnode)

    triplex_nodes = soup.gridlabd.powerflow.triplex_node_list
    nameofnode = triplex_nodes.findAll('name')
    node_processing(nameofnode)

    # EDGES

    oh_lines = soup.gridlabd.powerflow.overhead_line_list
    froms = oh_lines.findAll('from')
    tos = oh_lines.findAll('to')
    add_to_forms_and_tos(froms, tos)


    ug_lines = soup.gridlabd.powerflow.underground_line_list
    froms = ug_lines.findAll('from')
    tos = ug_lines.findAll('to')
    add_to_forms_and_tos(froms, tos)

    xfmrs = soup.gridlabd.powerflow.transformer_list
    froms = xfmrs.findAll('from')
    tos = xfmrs.findAll('to')
    add_to_forms_and_tos(froms, tos)

    triplex_lines = soup.gridlabd.powerflow.triplex_line_list
    froms = triplex_lines.findAll('from')
    tos = triplex_lines.findAll('to')
    add_to_forms_and_tos(froms, tos)

    regulators = soup.gridlabd.powerflow.regulator_list
    froms = regulators.findAll('from')
    tos = regulators.findAll('to')
    add_to_forms_and_tos(froms, tos)

    fuses = soup.gridlabd.powerflow.fuse_list
    froms = fuses.findAll('from')
    tos = fuses.findAll('to')
    add_to_forms_and_tos(froms, tos)

    switches = soup.gridlabd.powerflow.switch_list
    froms = switches.findAll('from')
    tos = switches.findAll('to')
    add_to_forms_and_tos(froms, tos)

    reclosers = soup.gridlabd.powerflow.recloser_list
    froms = reclosers.findAll('from')
    tos = reclosers.findAll('to')
    add_to_forms_and_tos(froms, tos)

    lines = soup.gridlabd.powerflow.line_list
    froms = lines.findAll('from')
    tos = lines.findAll('to')
    add_to_forms_and_tos(froms, tos)

    series_reactors= soup.gridlabd.powerflow.series_reactor_list
    froms = series_reactors.findAll('from')
    tos = series_reactors.findAll('to')
    add_to_forms_and_tos(froms, tos)

    sectionalizers = soup.gridlabd.powerflow.sectionalizer_list
    froms = sectionalizers.findAll('from')
    tos = sectionalizers.findAll('to')
    add_to_forms_and_tos(froms, tos)

    del froms,tos

    
    # TOTAL NUMBER OF NODES
    
    n_poles = calculate_real_value(len(poles))
    n_loads = calculate_real_value(len(loads))
    n_motors = calculate_real_value(len(motors))
    n_meters = calculate_real_value(len(meters))
    n_capacitors = calculate_real_value(len(capacitors))
    n_substations = calculate_real_value(len(substations))
    n_triplex_meters = calculate_real_value(len(triplex_meters))
    n_triplex_loads = calculate_real_value(len(triplex_loads))
    n_triplex_nodes = calculate_real_value(len(triplex_nodes))
    # n_loads is excluded from the addition below because load node and meter node is considered same
    total_nodes =  n_poles  + n_motors + n_meters + n_capacitors + n_substations + n_triplex_meters + n_triplex_loads + n_triplex_nodes

    # TOTAL NUMBER OF EDGES
    n_xfmrs = calculate_real_value(len(xfmrs))
    n_oh_lines = calculate_real_value(len(oh_lines))
    n_ug_lines = calculate_real_value(len(ug_lines))
    n_triplex_lines = calculate_real_value(len(triplex_lines))
    n_regulators = calculate_real_value(len(regulators))
    n_fuses = calculate_real_value(len(fuses))
    n_switches = calculate_real_value(len(switches))
    n_reclosers = calculate_real_value(len(reclosers))
    n_lines = calculate_real_value(len(lines))
    n_series_reactors= calculate_real_value(len(series_reactors))
    n_sectionalizers = calculate_real_value(len(sectionalizers))

    # TOTAL EDGES
    total_edges = n_sectionalizers+n_series_reactors+n_lines+n_reclosers+n_switches+n_fuses+n_regulators+n_triplex_lines+n_xfmrs+n_ug_lines+n_oh_lines
    # WRITING TO JSON FILES

    # METER INFORMATION
    meter_processing(meters, n_meters)

    # PRINTING OUTPUT
    print("----------------------------------------------")
    print("NODES")
    print("----------------------------------------------")
    print("Poles = ", n_poles) 
    print("Loads = ", n_loads) 
    print("Motors = ", n_motors) 
    print("Meters = ", n_meters) 
    print("Capacitors = ", n_capacitors) 
    print("Substation Nodes = ", n_substations) 
    print("Customer Metering Nodes = ", n_triplex_meters) 
    print("1-ph or 2-ph customers = ", n_triplex_loads) 
    print("1-ph or 2-ph customers nodes = ", n_triplex_nodes)
    print("----------------------------------------------")
    print("Total Number of Nodes = ", int(total_nodes))
    print("----------------------------------------------")
    print("EDGES")
    print("--------------------------------")
    print("Transformers = ", n_xfmrs)
    print("OH Lines = ", n_oh_lines)
    print("UG Lines = ", n_ug_lines)
    print("Lines to customers = ", n_triplex_lines)
    print("Regulators = ", n_regulators)
    print("Fuses = ", n_fuses)
    print("Switches = ", n_switches)
    print("Reclosers = ", n_reclosers)
    print("Lines = ", n_lines)
    print("Series Reactors = ", n_series_reactors)
    print("Sectionalizers = ", n_sectionalizers)
    print("--------------------------------")
    print("Total Number of Edges = ", int(total_edges))

## SAVE DATA FOR TRANSFORMERS

## SAVE DATA FOR NODES LIST

## SAVE DATA FOR METERS INFORMATION



# SAVE DATA FOR D3JS FORMAT
ff = open("data_for_d3js_plot.txt","w+")

ff.write("{\n\n\tnodes: [\n")
for n in allnodes:
	if allnodes.index(n)!=(total_nodes-1):
		ff.write("\t\tname: {%s},\n" % n)
	else:
		ff.write("\t\tname: {%s}\n\t\t]," % n)
ff.write("\n\tedges: [\n")
for f in allfroms:
	temp = allfroms.index(f)
	g = alltos[temp]
	print(type(f))
	print(type(g))
	if temp !=(total_edges-1):
		ff.write("\t\t{source: %s, target:},\n" % f)
	else:
		ff.write("\t\t{source: %s, target:}\n\t]\n}" % f)

ff.close()
del ff

# CREATE GRAPHS
print(allfroms, alltos)
print(allnodes)
G = nx.Graph()
for i in range(0, len(allfroms)):
	G.add_edge(allfroms[i],alltos[i])


f = plt.figure()
nx.draw(G, ax=f.add_subplot(111))
f.savefig("graph.png")
