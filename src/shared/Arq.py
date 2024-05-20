### All helper (shared) functions for Arq are defined here.
### It is going to be used by both the client and the server.

import struct
import binascii
import socket
import time
import sys
sys.path.insert(0, './shared') # this is for vs code debugging ;d 
from ArqPacket import ArqPacket

from shared.ArqPacket import ArqPacket
import RandomNumberGenerator as RNG

### GLOBAL VARIABLES ###
socket_buffer_size = 1024
arq_buffer_size = 16
arq_window_size = 16
timeout = 0.4 # time before calling timeout resending packet
latency = 0.2 # client and server will wait for 0.5 * latency seconds before sending packets
lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque ac porta ligula. Morbi semper venenatis ullamcorper. Quisque dignissim mi et vestibulum feugiat. Nam luctus nisl magna, eget imperdiet purus blandit sed. Proin et laoreet metus. Aenean et lacus ac lacus blandit interdum. Cras aliquam ipsum hendrerit aliquet egestas.Quisque vel augue dui. Mauris tristique posuere odio, in aliquam magna iaculis eget. Vestibulum ut dolor finibus, egestas enim eget, elementum felis. Mauris tempor erat justo, ac rutrum sem congue eget. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris pharetra gravida est eu tristique. Mauris eu est tincidunt, porta purus et, rutrum neque. Ut efficitur diam ac leo dictum dictum. Etiam justo massa, lacinia sed augue vel, interdum congue neque. Vivamus nulla sapien, iaculis eu ultrices nec, condimentum tempor orci. Proin ultricies quam lacus, consequat hendrerit dolor elementum vitae. Fusce ut elit a orci elementum imperdiet in ac arcu. Vivamus dignissim et ipsum mi."
pkt_loss = 10 # X% chance of packet loss
random_values = RNG.RandomNumberGenerator(1000, 1000).gen_numbers()

# remove this
random_values[0] = 0
random_values[1] = 0
random_values[2] = 0


socket.timeout=timeout

print('t2')

def generateLatency():
    # Function that generates network laterncy, for example it can just sleep for a x amount of time
    pass


def generatePacketLoss(index):
    # return true if packet loss should occur. 

    if (random_values[index] < pkt_loss*10):
        return True
    else:
        return False
        





def reassembleMsg(msg_dict):
    msg = b""
    checksum_check = True
    cheksum = struct.unpack('>I',msg_dict[0])[0]
    seq = 1
    while seq in msg_dict:
        msg += msg_dict[seq]
        seq += 1

    if (binascii.crc32(msg) != cheksum):
        print(f"Checksum failed")
        checksum_check = False
    return msg, checksum_check


def printDict(msg_dict):
    for key in msg_dict:
        print(f"Seq: {key} data: {msg_dict[key]}")



def sendMsgSeq(s, bytes_sent, seq, msg, buffer_size, host, port):
    # Adding sleep here to simulate network latency
    time.sleep(latency//2)

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
            print(f"Timeout, resending checksum: {checksum}")
            s.sendto(packet, (host, port))
            if (tout_count > 6):
                print("Too many timeouts, disconnecting")
                recv_buffer = False
            continue


def startTransmission(s, buffer_size, HOST, PORT):
    connected = False
    print('trying connect')
    while (not connected):

        s.sendto(ArqPacket(1, 3, 1, b"SYN").toBytes(), (HOST, PORT))
        while True:
            try:
                data, addr = s.recvfrom(buffer_size)
                recv_packet = ArqPacket.fromBytes(data)
                print(recv_packet)
                if (recv_packet.pck_type == 1 and recv_packet.msg_type == 4):
                    print(f"Received SYN-ACK: {recv_packet}")
                    print('connected')
                    connected = True
                    return connected
                else:
                    print(f"Received packet: {recv_packet}")
            except TimeoutError:
                print('Timeout while connecting')
                break
    

    print('connected')
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
            print("Timeout, Resending FIN")
            s.sendto(ArqPacket(1,5,-1,b"FIN").toBytes(), (HOST, PORT))
            if (tout_count > 4):
                print("Too many timeouts, disconnecting")

                recv_buffer = False
            continue
