import socket
import struct
import sys
import threading
sys.path.insert(0, './shared')
from ArqPacket import ArqPacket
import Arq as Arq

#rom shared.ArqPacket import * 
#import shared.Arq as Arq
import binascii


#### GLOBAL SETTINGS !
HOST = "localhost"  # The server's hostname or IP address
PORT = 65432        # Port for data
buffer_size = Arq.arq_buffer_size
window_size = Arq.arq_window_size # window size for sliding window protocol must be the same on both sides
bytes_sent = 0 
seq_bytes_dict = {} # dict of seq number and bytes sent
#### GLOBAL SETTINGS

def handle_packet(data, addr):
    print(f"Received data message: {data.decode()} from {addr}")



def handle_ack(s):
    global bytes_sent
    global seq_bytes_dict
    print("Waiting for ack")
    while seq_sent:
        try:
            data, addr = s.recvfrom(buffer_size)
            recv_packet = ArqPacket.fromBytes(data)

            if (recv_packet.msg_type == 1):
                print(f"Received ACK message: {recv_packet} from {addr}")
                bytes_sent += seq_bytes_dict[recv_packet.seq] 
                seq_sent.remove(recv_packet.seq)
                continue
            elif (recv_packet.msg_type == 2):
                print(f"Received NACK from {addr}, resending packet seq {recv_packet.seq}")
                continue
            else:
                print(f"Received management message: {recv_packet} from {addr}")
                continue
        except socket.timeout:
            print("Timeout, resending packet seq {seq}")
            Arq.sendMsgSeq(s,bytes_sent,seq,message,buffer_size,HOST,PORT)
            #tout_count += 1
            # if (tout_count > 3):
            #     print("Too many timeouts, resending packet seq {seq}")
            recv_buffer = False
            break




if __name__ == "__main__":
    message = Arq.lorem.encode()
    #message = " msg from client that exceeds buffer for sure! and exceeds one slidin window as well!!".encode()


    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

        print(f"Client started, using server {HOST} data port:{PORT}")  
        
        # We have to create a connection between client and server. 
        # Send REQ packet and wait for REQ-ACK before sending any data.
        # TODO: Finish the implementation        

        connected = Arq.startTransmission(s,buffer_size,HOST,PORT)

        # We have to divide the message into chunks, because the buffer size is limited
        # Every new chunk sent will increase the sequence number
        # Thanks to that sequence number, the server will be able to reconstruct the message even if it got in different order
        # Server will save chunks into dictionary, so it is easy to reconstruct

        #bytes_sent = 0
        seq = 1 
        s.settimeout(0.2)
        ack_count = 0

        seq_sent = [] # list of sent seq numbers in this window
        msg_len = len(message)
        Arq.sendChecksum(s,message,buffer_size,HOST,PORT) # send checksum of the whole message. We are not going to proceed unitl this is sent and acknowledged.
        
        

        while bytes_sent < len(message):
            tout_count = 0
            ack_watch_thread = threading.Thread(target=handle_ack,args=(s,))
            ack_watch_thread.start()
            for i in range(window_size):
                if (bytes_sent + i*buffer_size >= len(message)):
                    break
                chunk_len, _ = Arq.sendMsgSeq(s,bytes_sent,seq,message,buffer_size,HOST,PORT)
                seq_bytes_dict[seq] = chunk_len
                seq_sent.append(seq)
                seq += 1
            ## Start thread that looks for ACKs

            ack_watch_thread.join()
             # Wait for ACK
  #              recv_buffer = True            
  #              while recv_buffer == True:
  #                  try:
  #                      data, addr = s.recvfrom(buffer_size)
  #                      packet = ArqPacket.fromBytes(data)

  #                      if (packet.msg_type == 1):
  #                          print(f"Received ACK message: {packet} from {addr}")
  #                          seq_sent.remove(packet.seq)
  #                          bytes_sent += seq_bytes_dict[packet.seq] 
  #                          continue
  #                      elif (packet.msg_type == 2):
  #                          print(f"Received NACK from {addr}, resending packet seq {packet.seq}")
  #                          continue
  #                      else:
  #                          print(f"Received management message: {packet} from {addr}")
  #                          continue
  #                  except socket.timeout:
  #                      print("Timeout")
  #                      tout_count += 1
  #                      # if (tout_count > 3):
  #                      #     print("Too many timeouts, resending packet seq {seq}")
  #                      recv_buffer = False
  #                      break
            


        ack_watch_thread.join()
        

        #EndTransmission
        Arq.endTransmission(s, buffer_size, HOST, PORT)



