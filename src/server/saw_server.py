import socket
import threading
from shared.ArqPacket import ArqPacket
import time

HOST = "localhost"  # Standard loopback interface address (localhost)
PORT = 65432        # Port for data
buffer_size = 1024

message = b"Hello, msg from server!"
msg_dict = {}


def print_dict(msg_dict):
    for key in msg_dict:
        print(f"Seq: {key} data: {msg_dict[key]}")


def handle_packet(data, addr):
    packet = ArqPacket.from_bytes(data)

    if (packet.msg_type == 0): # If this is data message, we are going to add this do the dict
        if packet.check_checksum():
            msg_dict[packet.seq] = packet.data
            #time.sleep(3)
            # Send ACK
            s.sendto(ArqPacket(1, 1, packet.seq, b"ACK").to_bytes(), addr)
            print(f"Sending ACK to {addr}")
        else:
            print(f"Checksum failed for packet {packet}")
            s.sendto(ArqPacket(1, 2, packet.seq, b"NACK").to_bytes(), addr)

    elif (packet.msg_type == 3):
        print(f"Received SYN message: {str(packet)} from {addr}")
        #Clear dict // T is only temporary solution, later smth bettwe will be implemented
        #So we are assembling new transmission message
        msg_dict.clear()
        # Send SYN-ACK
        s.sendto(ArqPacket(1, 4, 1, b"SYN-ACK").to_bytes(), addr)


    elif (packet.msg_type == 5):
        print(f"Received FIN message: {str(packet)} from {addr}")
        # Send FIN-ACK
        s.sendto(ArqPacket(1, 6, 1, b"FIN-ACK").to_bytes(), addr)
        print_dict(msg_dict)    # ended transmission so we can assemble the message


    else:
        print(f"Received unhandled message: {str(packet)} from {addr}")



    print(f"Received data message: {str(packet)} from {addr}")

def handle_data_stream(s_data):
    while True:
        print("Waiting for data")
        data, addr = s_data.recvfrom(buffer_size)
        handle_packet(data, addr)



if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:


        

        print(f"Server started, data port:{PORT}")  
        s.bind((HOST, PORT))

        data_thread = threading.Thread(target=handle_data_stream, args=(s,))

        data_thread.start()

        data_thread.join()

