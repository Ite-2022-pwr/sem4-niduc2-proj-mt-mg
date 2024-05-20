import socket
import struct
import binascii
import threading

import sys
# sys.path.insert(0, './shared')
# from ArqPacket import ArqPacket
# import Arq as Arq

from shared.ArqPacket import ArqPacket
import shared.Arq as Arq
import time

HOST = "localhost"  # Standard loopback interface address (localhost)
PORT = 65433        # Port for data
socket_buffer_size = 1024
window_size = Arq.arq_window_size  # window size for sliding window protocol must be the same on both sides
message = b"Hello, msg from server!"
msg_dict = {}




i  = -1
def handle_packet(data, addr):
    global msg_dict
    global st1
    global i 
    packet = ArqPacket.fromBytes(data)
    time.sleep(Arq.latency//2)

    # Just to prevent out of bounds
    if (i >= Arq.random_values.__len__()):
        i = 0 

    i += 1
    ## packet loss
    if Arq.generatePacketLoss(i):
        print(f"Packet loss for packet {packet}")
        return



    st = time.time()
    if packet.checkChecksum():
        msg_dict[packet.seq] = packet.getData()   
        s.sendto(ArqPacket(1, 1, packet.seq, b"ACK").toBytes(), addr)
        print(f"Sending ACK {str(packet)} to {addr}")
        if (packet.msg_type == 0): # If this is data message, we are going to add this do the dict
            if (packet.seq > 0 and (packet.seq-1 not in msg_dict)):
                # current sequence does not match our expected sequence, therefore we are missing at least previous packet.
                s.sendto(ArqPacket(1, 2, packet.seq-1, b"NACK").toBytes(), addr)
                print(f"Sending NACK for {packet.seq-1} to {addr}")

        elif (packet.msg_type == 3):
            print(f"Received SYN message: {str(packet)} from {addr}")
            #Clear dict // T is only temporary solution, later smth bettwe will be implemented
            #So we are assembling new transmission message
            msg_dict.clear()
            st1 = time.time()
            # Send SYN-ACK
            s.sendto(ArqPacket(1, 4, 1, b"SYN-ACK").toBytes(), addr)


        elif (packet.msg_type == 5):
            print(f"Received FIN message: {str(packet)} from {addr}")
            # Send FIN-ACK
            # Reassmble message
            reassembled_msg, checksum_check = Arq.reassembleMsg(msg_dict)
            if (checksum_check):
                print(f"Checksum check passed")
                s.sendto(ArqPacket(1, 6, 1, b"FIN-ACK").toBytes(), addr)
                print(f"Received msg in {(time.time()-st1) * 1000} ms")
            print(f"Reassembled message: {Arq.reassembleMsg(msg_dict)}")
            # Arq.printDict(msg_dict)    # ended transmission so we can assemble the message
            msg_dict.clear()
        
        else:
            print(f"Received unhandled message: {str(packet)} from {addr}")

    else:
        print(f"Checksum failed for packet {packet}")
        s.sendto(ArqPacket(1, 2, packet.seq, b"NACK").toBytes(), addr)

    print(f"Received data message: {str(packet)} from {addr}")
    print(f"Packet handled in: {(time.time()-st) * 1000} ms")

def handle_data_stream(s_data):
    while True:
        print("Waiting for data")
        data, addr = s_data.recvfrom(socket_buffer_size)
        handle_packet(data, addr)



if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:


        

        print(f"Server started, data port:{PORT}")  
        s.bind((HOST, PORT))
        while True:
            print("Waiting for data")
            data, addr = s.recvfrom(socket_buffer_size)
            handle_packet(data, addr)

        # data_thread = threading.Thread(target=handle_data_stream, args=(s,))

        # data_thread.start()

        # data_thread.join()

