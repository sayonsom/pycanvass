import socket
import sys
import time
from collections import defaultdict
import json
import csv
import pycanvass.global_variables as gv
import pycanvass.blocks as blocks
from scapy.all import *

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class CyberNode:
    """
    A class that represents the cyber capabilities of any node in the network.
    Can be auto-generated in a cyber-physical model, or explicitly generated.
    """

    def __init__(self, name, ip, port, protocol, encryption, CVSS, firewall):
        self.name = name
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.encryption = encryption
        self.CVSS = CVSS
        self.firewall = firewall


def setup_new_device(cyber_node_name, ip_value, port_value, protocol_name, cvss = None, firewall = False):

    cyber_node = CyberNode(name=cyber_node_name,
                           ip=ip_value,
                           port=port_value,
                           protocol=protocol_name,
                           CVSS=None,
                           firewall=False,
                           encryption=False)
    return cyber_node


def pair_devices(from_device, to_device, protocol, handshake=False, direction="bidirectional"):
    """

    :param from_device:
    :param to_device:
    :param direction:
    :return:
    """

    src_ip = from_device.ip
    src_port = from_device.port
    dst_ip = to_device.ip
    dst_port = to_device.port
    try:
        packet = IP(dst=dst_ip) / TCP() / "Test Connection"
        uans, ans = sr(packet)
        print(ans.summary())
        print(uans.summary())
        if handshake is True:
            try:
                print("[i] Confirming TCP connection with 3-way handshake")
                hostname = socket.gethostname()
                ip_address_of_host_computer = socket.gethostbyname(hostname)

                sport = random.randint(1024, 65535)
                print("[i] IP Address of host computer = {} : {}".format(ip_address_of_host_computer, sport))
                print("[i] IP Address of destination computer = {} : {}".format(dst_ip, dst_port))
                # SYN
                ip = IP(src=ip_address_of_host_computer, dst=dst_ip)
                SYN = TCP(sport=sport, dport=dst_port, flags='S', seq=1000)
                SYNACK = sr1(ip / SYN)

                # SYN-ACK
                ACK = TCP(sport=sport, dport=dst_port, flags='A', seq=SYNACK.ack + 1, ack=SYNACK.seq + 1)
                send(ip / ACK)
            except:
                print("[i] Check TCPDUMP on Terminal ('netsh' on Windows) or, WireShark")

    except:
        print("[x] Failed to pair {} and {}".format(from_device.name, to_device.name))


def send_data_packet(to_device, payload="100", protocol="TCP"):
    """
    This function sends data.
    :param name:
    :param payload:
    :param protocol: Default protocol used in TCP/IP
    :return:
    """

    if to_device.ip == "" or to_device.port == "":
        print("[x] Device IP Address or Port is empty, disconnected, or improperly configured.")
        print("[i] Please refer to documentation, or ask Sayon: sayon@ieee.org")
        raise ConnectionError

    if protocol == "TCP":
        packet = IP(dst=to_device.ip / TCP() / Raw(load=payload))
    try:
        sendp(packet)
        print(packet.summary())
    except:
        print("Failed to send data packet.")


# Connect the socket to the port where the server is listening
def connect(device, ip_addr, port, polling_interval=1):
    server_address = (ip_addr, int(port))
    sock.connect(server_address)
    i = 0
    while i < 50:
        sock.sendall("Hello {}. This is Msg {}.\n".format(device, i))
        data = sock.recv(1024)
        if data:
            print("Received from {} --> {}".format(device, data))
            switch_status_dict = json.loads(data)
            for k, v in switch_status_dict.items():
                print("key = {}, value = {}".format(k, v))
        else:
            print("No data received from {}".format(device))
            break
        time.sleep(polling_interval)
        i += 1
    sock.close()

def _print_data_packet(packet):
    print("Received Data Packet")
    print(packet.summary())

def get_data(device_name):
    filter_statement = device_name.protocol + " and " + device_name.ip + " port " + device_name.port
    sniff(filter=filter_statement, prn=_print_data_packet, count=3)

def connect_and_control(device, ip_addr, port, polling_interval=1):
    """

    :return:
    """
    server_address = (ip_addr, int(port))
    try:
        sock.connect(server_address)
        sock.sendall("CANVASS CONNECTED: Hello {}!\n".format(device))
    except:
        print("[x] May be {} is not turned on, and set up to send data as a server".format(device))
        return False

    i = 0
    while i < 500000:
        data = sock.recv(1024)
        if data:
            print("Received from {} --> {}".format(device, data))
            sock.sendall("ACK".encode("utf-8"))
            switch_status_dict = json.loads(data)
            for k, v in switch_status_dict.items():
                print("Edge search result = {}".format(_edge_search(k)))
                edit_edge_status(k, flip_status=1)


        else:
            print("No data received from {}".format(device))
            break
        time.sleep(polling_interval)
        i += 1
    sock.close()
    network = blocks.rebuild()
    return network


def _edge_search(e):
    e_file = gv.filepaths["edges"]
    with open(e_file) as f:
        counter = 0
        match_flag = 0
        edges = csv.reader(f)
        for edge in edges:
            counter += 1
            if edge[0].lstrip() == e:
                match_flag = 1
                return counter - 1

        if match_flag == 0:
            print("[x] Edge could not be found.")
            return 0


def edit_edge_status(edge_name, flip_status=0):
    new_rows = []
    e_file = gv.filepaths["edges"]
    edge_search_result = _edge_search(edge_name)
    with open(e_file, 'r+') as f:
        csvr = csv.reader(f)
        csvr = list(csvr)
        for row in csvr:
            new_row = row
            if row[0].lstrip() == edge_name and edge_search_result != 0:
                print("Status of %s is %s" % (edge_name, row[4]))
                if flip_status == 1:
                    if row[4].lstrip() == "1":
                        print("Changing status from ON to OFF.")
                        new_row[4] = "0"

                    else:
                        print("Changing status from OFF to ON.")
                        new_row[4] = "1"


            else:
                print("Edge not found")

            new_rows.append(new_row)

    with open(e_file, 'wb') as f:
        # Overwrite the old file with the modified rows
        writer = csv.writer(f)
        writer.writerows(new_rows)
