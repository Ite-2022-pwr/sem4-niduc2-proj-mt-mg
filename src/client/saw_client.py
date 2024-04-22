import socket
import sys
sys.path.insert(0, './shared')
from ArqPacket import ArqPacket
import Arq as Arq


# from shared.ArqPacket import ArqPacket
# import shared.Arq as Arq


HOST = "localhost"  # The server's hostname or IP address
PORT = 65432        # Port for data
arq_buffer_size = Arq.arq_buffer_size




def handle_packet(data, addr):
    print(f"Received data message: {data.decode()} from {addr}")



if __name__ == "__main__":
    message = Arq.lorem.encode()
    #message = "Hello, msg from client that exceeds buffer for sure!".encode()


    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

        print(f"Client started, using server {HOST} data port:{PORT}")  
        
        # We have to create a connection between client and server. 
        # Send REQ packet and wait for REQ-ACK before sending any data.
        # TODO: Finish the implementation        

        connected = Arq.startTransmission(s,arq_buffer_size,HOST,PORT)

        # We have to divide the message into chunks, because the buffer size is limited
        # Every new chunk sent will increase the sequence number
        # Thanks to that sequence number, the server will be able to reconstruct the message even if it got in different order
        # Server will save chunks into dictionary, so it is easy to reconstruct

        bytes_sent = 0
        seq = 1 
        s.settimeout(Arq.timeout)

        Arq.sendChecksum(s,message,arq_buffer_size,HOST,PORT) # send checksum of the whole message. We are not going to proceed unitl this is sent and acknowledged.


        while bytes_sent < len(message):
            tout_count = 0
            
            chunk_len, packet_len = Arq.sendMsgSeq(s,bytes_sent,seq,message,arq_buffer_size,HOST,PORT)
            # Wait for ACK
            while True:
                try:
                    data, addr = s.recvfrom(arq_buffer_size)
                    packet = ArqPacket.fromBytes(data)
                    print(f"Received : {packet}")

                    if (packet.msg_type == 1):
                        print(f"Received ACK message: {packet} from {addr}")
                        bytes_sent += chunk_len
                        seq += 1
                        break
                    elif (packet.msg_type == 2):
                        print(f"Received NACK from {addr}, resending packet seq {packet.seq}")
                        break
                    else:
                        print(f"Received management message: {packet} from {addr}")
                except socket.timeout:
                    print("Timeout")
                    print(f"Resending packet seq {seq}")
                    break
        


        
        ### END OF TRANSMISION, send FIN msg
        Arq.endTransmission(s,arq_buffer_size,HOST,PORT)



