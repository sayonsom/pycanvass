from scapy.all import *
import BER

class GOOSE(Packet):
    name = "GOOSE"
    fields_desc = [ ShortField("APPID", 0x3000),
                    ShortField("Length", 0),
                    ShortField("Reserved1", 0),
                    ShortField("Reserved2", 0),
                  ]