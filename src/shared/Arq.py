### All helper (shared) functions for Arq are defined here.
### It is going to be used by both the client and the server.

import struct
import binascii
import socket
import time
import sys
sys.path.insert(0, './shared') # this is for vs code debugging ;d 
from ArqPacket import ArqPacket

#from shared.ArqPacket import ArqPacket


### GLOBAL VARIABLES ###
socket_buffer_size = 1024
socket_timeout = 0.5
arq_buffer_size = 16
arq_window_size = 5
lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer mi ante, ultrices molestie bibendum ut, accumsan ut metus. In ac maximus erat. Aliquam porta, magna id convallis euismod, nunc tellus blandit ipsum, vel bibendum tortor urna ac nulla gravida."





def generateLatency():
    # Function that generates network laterncy, for example it can just sleep for a x amount of time
    
    pass


def generatePacketLoss():
    # Function that generates packet loss, for example it can just not send a packet
    # it can utilize our RNG to determine if a packet is lost or not
    pass




def reassembleMsg(msg_dict):
    msg = b""
    cheksum = struct.unpack('>I',msg_dict[0])[0]
    seq = 1
    while seq in msg_dict:
        msg += msg_dict[seq]
        seq += 1

    if (binascii.crc32(msg) != cheksum):
        print(f"Checksum failed")
    return msg


def printDict(msg_dict):
    for key in msg_dict:
        print(f"Seq: {key} data: {msg_dict[key]}")



def sendMsgSeq(s, bytes_sent, seq, msg, buffer_size, host, port):
    chunk = msg[(seq-1)*buffer_size:seq*buffer_size]
    packet = ArqPacket(0, 0, seq, chunk).toBytes()
    s.sendto(packet, (host, port))
    print(f"Sent {bytes_sent} msg bytes: {chunk}")
    print(f"Packet size: {len(packet)}")
    return len(chunk),len(packet) 



def sendChecksum(s, msg, buffer_size, host, port):
    checksum = struct.pack('>I',binascii.crc32(msg))
    packet = ArqPacket(0, 0, 0, checksum).toBytes()
    s.sendto(packet, (host, port))
    print(f"Sent checksum: {checksum}")
    recv_buffer = True
    tout_count = 0
    while recv_buffer == True:
        try:
            data, addr = s.recvfrom(buffer_size)
            recv_packet = ArqPacket.fromBytes(data)
            if (recv_packet.msg_type == 1 and recv_packet.seq == 0):
                print(f"Received ACK for checksum: {recv_packet}")
                return
            elif (recv_packet.msg_type == 2 and recv_packet.seq == 0):
                print(f"Received NACK for checksum: {recv_packet}")
                s.sendto(packet,addr) 
                print(f"Resent checksum: {checksum}")
            else:
                print(f"Received packet: {recv_packet}")
        except socket.timeout:
            tout_count += 1
            print("Timeout")
            if (tout_count > 3):
                print("Too many timeouts, resending checksum")
                recv_buffer = False
            continue


def startTransmission(s, buffer_size, HOST, PORT):
    connected = False
    while (not connected):

        s.sendto(ArqPacket(1, 3, 1, b"SYN").toBytes(), (HOST, PORT))
        recv_buffer = True
        tout_count = 0
        while recv_buffer == True:
            try:
                data, addr = s.recvfrom(buffer_size)
                recv_packet = ArqPacket.fromBytes(data)
                if (recv_packet.pck_type == 1 and recv_packet.msg_type == 4):
                    print(f"Received SYN-ACK: {recv_packet}")
                    return
                else:
                    print(f"Received packet: {recv_packet}")
            except socket.timeout:
                tout_count += 1
                print("Timeout")
                if (tout_count > 3):
                    print("Too many timeouts, resending SYN")
                    recv_buffer = False
                continue
    return connected


def endTransmission(s, buffer_size, HOST, PORT):
    s.sendto(ArqPacket(1,5,-1,b"FIN").toBytes(), (HOST, PORT))
    print("Sent FIN msg")
    recv_buffer = True
    tout_count = 0
    while recv_buffer == True:
        try:
            data, addr = s.recvfrom(buffer_size)
            recv_packet = ArqPacket.fromBytes(data)
            if (recv_packet.pck_type == 1 and recv_packet.msg_type == 6):
                print(f"Received FIN-ACK: {recv_packet}")
                return
            else:
                print(f"Received packet: {recv_packet}")
        except socket.timeout:
            tout_count += 1
            print("Timeout")
            if (tout_count > 3):
                print("Too many timeouts, resending FIN")
                recv_buffer = False
            continue
