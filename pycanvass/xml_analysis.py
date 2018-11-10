from bs4 import BeautifulSoup



def voltage_profile(nodes, filename=None, mode=""):
    if filename is not None:
        fp = filename
    else:
        fp = 'gridlabd.xml'
    soup = BeautifulSoup(fp,'lxml')
    node_soup = soup.gridlabd.powerflow.node_list
    nodes_to_search = []
    
    if type(nodes) is array:
        nodes_to_search = nodes
    
