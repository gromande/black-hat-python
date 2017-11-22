import socket
import os
import struct
from ctypes import *

#host to listen on
host = "10.0.2.15"

#our ip header
class IP(Structure):

    #This is annoying but you have to specify the bytes
    #to make sure it works in every platform
    #see: https://stackoverflow.com/questions/29306747
    _fields_ = [
        ("ihl",         c_ubyte, 4),
        ("version",     c_ubyte, 4),
        ("tos",         c_ubyte),
        ("len",         c_ushort),
        ("id",          c_ushort),
        ("offset",      c_ushort),
        ("ttl",         c_ubyte),
        ("protocol_num",c_ubyte),
        ("sum",         c_ushort),
        ("src",         c_uint32),
        ("dst",         c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        #map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        #human readable IP address
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        #human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):

    _fields_ = [
        ("type",        c_ubyte),
        ("code",        c_ubyte),
        ("checksum",    c_ushort),
        ("unused",      c_ushort),
        ("next_hop_mtu",c_ushort)
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

#create a raw socket an bind it to the public interface
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

sniffer.bind((host, 0))

#we want the IP header included in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

try:
    while True:
        raw_buffer = sniffer.recvfrom(65535)[0]

        #create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[:20])

        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address,
                                     ip_header.dst_address))

        if ip_header.protocol == "ICMP":

            #calculate where our ICMP packet starts
            offset = ip_header.ihl * 4
            icmp_buffer = raw_buffer[offset:offset + sizeof(ICMP)]

            #create our ICMP structure
            icmp_header = ICMP(icmp_buffer)

            print("ICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))
except KeyboardInterrupt:
    pass
