import socket
import struct
import sys
import threading
sys.path.insert(0, './shared')
from ArqPacket import ArqPacket
import Arq as Arq

from shared.ArqPacket import * 
import shared.Arq as Arq
import binascii


#### GLOBAL SETTINGS !
HOST = "localhost"  # The server's hostname or IP address
PORT = 65433        # Port for data
buffer_size = Arq.arq_buffer_size
window_size = Arq.arq_window_size # window size for sliding window protocol must be the same on both sides
bytes_sent = 0 
seq_bytes_dict = {} # dict of seq number and bytes sent
seq_sent = []# list of sent seq numbers in this window
packets_sent = 0
#### GLOBAL SETTINGS

def handle_packet(data, addr):
    pass
    #print(f"Received data message: {data.decode()} from {addr}")



def handle_ack(s):
    global bytes_sent
    global seq_bytes_dict
    global seq_sent
    global packets_sent
    #print("Waiting for ack")
    loop = True
    while seq_sent:
            try:
                data, addr = s.recvfrom(buffer_size)
                recv_packet = ArqPacket.fromBytes(data)
                if (recv_packet.pck_type == 1):
                    if (recv_packet.msg_type == 1):
                        #print(f"Received ACK message: {recv_packet} from {addr}")
                        bytes_sent += seq_bytes_dict[recv_packet.seq] 
                        if (recv_packet.seq in seq_sent):
                            seq_sent.remove(recv_packet.seq)
                        continue
                    elif (recv_packet.msg_type == 2):
                        #print(f"Received NACK from {addr}, resending packet seq {recv_packet.seq}")
                        Arq.sendMsgSeq(s,bytes_sent,recv_packet.seq,message,buffer_size,HOST,PORT)
                        packets_sent += 1
                    elif (recv_packet.msg_type == 6):
                        #print(f"Received FIN-ACK from {addr}")
                        loop = False
                    else:
                        #print(f"Received management message: {recv_packet} from {addr}")
                        continue
            except TimeoutError:
                #print(f"Timeout. Resending packet seq {seq_sent[0]}")
                Arq.sendMsgSeq(s,bytes_sent,seq_sent[0],message,buffer_size,HOST,PORT)
                packets_sent += 1
                continue


if __name__ == "__main__":

    message = Arq.lorem.encode()
    #message = " msg from client that exceeds buffer for sure! and exceeds one slidin window as well!!".encode()


    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(Arq.timeout)
        #print(f"Client started, using server {HOST} data port:{PORT}")  

        connected = Arq.startTransmission(s,buffer_size,HOST,PORT)

        # We have to divide the message into chunks, because the buffer size is limited
        # Every new chunk sent will increase the sequence number
        # Thanks to that sequence number, the server will be able to reconstruct the message even if it got in different order
        # Server will save chunks into dictionary, so it is easy to reconstruct

        seq = 1 
        ack_count = 0

        msg_len = len(message)

        Arq.sendChecksum(s,message,buffer_size,HOST,PORT)
        packets_sent += 1
        while bytes_sent < len(message):
            tout_count = 0

            for i in range(window_size):
                if (bytes_sent + i*buffer_size >= len(message)):
                    break
                seq_sent.append(seq)
                seq += 1
            for tmp in seq_sent:
                chunk_len, _ = Arq.sendMsgSeq(s,bytes_sent,tmp,message,buffer_size,HOST,PORT)
                packets_sent += 1
                seq_bytes_dict[tmp] = chunk_len
            handle_ack(s)



        #EndTransmission
        Arq.endTransmission(s, buffer_size, HOST, PORT)
        packets_sent += 1
        print(f"{packets_sent},{msg_len//buffer_size}")



