import socket
import struct
import sys
sys.path.insert(0, './shared')
from ArqPacket import ArqPacket
import binascii



HOST = "localhost"  # The server's hostname or IP address
PORT = 65432        # Port for data
buffer_size = 16
window_size = 4 # window size for sliding window protocol must be the same on both sides



def handle_packet(data, addr):
    print(f"Received data message: {data.decode()} from {addr}")


def sendMsgSeq(s,bytes_sent,seq,msg,host,port):
    chunk = msg[(seq-1)*buffer_size:seq*buffer_size]
    packet = ArqPacket(0, 0, seq, chunk).to_bytes()
    s.sendto(packet, (host, port))
    print(f"Sent {bytes_sent} msg bytes: {chunk}")
    print(f"Packet size: {len(packet)}")
    return len(chunk),len(packet) 



def sendChecksum(msg, host, port):
    checksum = struct.pack('>I',binascii.crc32(msg))
    packet = ArqPacket(0, 0, 0, checksum).to_bytes()
    s.sendto(packet, (host, port))
    print(f"Sent checksum: {checksum}")
    recv_buffer = True
    tout_count = 0
    while recv_buffer == True:
        try:
            data, addr = s.recvfrom(buffer_size)
            recv_packet = ArqPacket.from_bytes(data)
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




if __name__ == "__main__":
    message = "Hello, msg from client that exceeds buffer for sure! and exceeds one slidin window as well!!".encode()


    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

        print(f"Client started, using server {HOST} data port:{PORT}")  
        
        # We have to create a connection between client and server. 
        # Send REQ packet and wait for REQ-ACK before sending any data.
        # TODO: Finish the implementation        
        connected = False

        while (not connected):
            s.sendto(ArqPacket(1, 3, 1, b"SYN").to_bytes(), (HOST, PORT))
            data, addr = s.recvfrom(buffer_size)
            packet = ArqPacket.from_bytes(data)
            if (packet.msg_type == 4):
                print(f"Received SYN-ACK message: {packet} from {addr}")
                connected = True


        # We have to divide the message into chunks, because the buffer size is limited
        # Every new chunk sent will increase the sequence number
        # Thanks to that sequence number, the server will be able to reconstruct the message even if it got in different order
        # Server will save chunks into dictionary, so it is easy to reconstruct

        bytes_sent = 0
        seq = 1 
        s.settimeout(0.5)
        ack_count = 0
        seq_bytes_dict = {} # dict of seq number and bytes sent
        seq_sent = [] # list of sent seq numbers in this window
        msg_len = len(message)
        sendChecksum(message,HOST,PORT) # send checksum of the whole message. We are not going to proceed unitl this is sent and acknowledged.

        while bytes_sent < len(message):
            tout_count = 0
            for i in range(window_size):
                seq_sent.append(seq)
                seq += 1
                if (bytes_sent + i*buffer_size >= len(message)):
                    break
            while seq_sent:
                for seq in seq_sent:
                   chunk_len, _ = sendMsgSeq(s,bytes_sent,seq,message,HOST,PORT)
                   seq_bytes_dict[seq] = chunk_len
            # Wait for ACK
                recv_buffer = True            
                while recv_buffer == True:
                    try:
                        data, addr = s.recvfrom(buffer_size)
                        packet = ArqPacket.from_bytes(data)

                        if (packet.msg_type == 1):
                            print(f"Received ACK message: {packet} from {addr}")
                            seq_sent.remove(packet.seq)
                            bytes_sent += seq_bytes_dict[packet.seq] 
                            continue
                        elif (packet.msg_type == 2):
                            print(f"Received NACK from {addr}, resending packet seq {packet.seq}")
                            continue
                        else:
                            print(f"Received management message: {packet} from {addr}")
                            continue
                    except socket.timeout:
                        print("Timeout")
                        tout_count += 1
                        # if (tout_count > 3):
                        #     print("Too many timeouts, resending packet seq {seq}")
                        recv_buffer = False
                        break
            


        
        ### END OF TRANSMISION, send FIN msg

        #EndTransmission
        s.sendto(ArqPacket(1, 5, 1, b"FIN").to_bytes(), (HOST, PORT))



