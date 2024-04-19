import socket
import threading
from shared.ArqPacket import ArqPacket
import time

HOST = "localhost"  # Standard loopback interface address (localhost)
PORT_data = 65432        # Port for data
PORT_mgn = 65433       # Port for management msg (for example, ACK)
buffer_size = 1024

message = b"Hello, msg from server!"
msg_dict = {}


def print_dict(msg_dict):
    for key in msg_dict:
        print(f"Seq: {key} data: {msg_dict[key]}")


def handle_management(data, addr):
    packet = ArqPacket.from_bytes(data)
    if (packet.msg_type == 3):
        print(f"Received REQ message: {str(packet)} from {addr}")
        #Clear dict // This is only temporary solution, later smth bettwe will be implemented
        #So we are assembling new transmission message
        msg_dict.clear()



        # Send REQ-ACK
        s_mgn.sendto(ArqPacket(1, 4, 1, b"REQ-ACK").to_bytes(), addr)
    elif (packet.msg_type == 5):
        print(f"Received FIN message: {str(packet)} from {addr}")
        print_dict(msg_dict)

        # Send FIN-ACK
        s_mgn.sendto(ArqPacket(1, 6, 1, b"FIN-ACK").to_bytes(), addr)
    else:

        print(f"Received management message: {str(packet)} from {addr}")


def handle_data(data, addr):
    packet = ArqPacket.from_bytes(data)
    if (packet.msg_type == 0): # If this is data message, we are going to add this do the dict
        msg_dict[packet.seq] = packet.data
        time.sleep(3)
        # Send ACK
        s_mgn.sendto(ArqPacket(1, 1, packet.seq, b"ACK").to_bytes(), addr)
        print(f"Sending ACK to {addr}")





    print(f"Received data message: {str(packet)} from {addr}")

def handle_data_stream(s_data):
    while True:
        print("Waiting for data")
        data, addr = s_data.recvfrom(buffer_size)
        handle_data(data, addr)

def handle_management_stream(s_mgn):
    while True:
        print("Waiting for management")
        data, addr = s_mgn.recvfrom(buffer_size)
        handle_management(data, addr)



if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_data, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s_mgn:


        

        print(f"Server started, data port:{PORT_data} management port:{ PORT_mgn}")  
        s_data.bind((HOST, PORT_data))
        s_mgn.bind((HOST, PORT_mgn))


        data_thread = threading.Thread(target=handle_data_stream, args=(s_data,))
        mgn_thread = threading.Thread(target=handle_management_stream, args=(s_mgn,))

        data_thread.start()
        mgn_thread.start()

        data_thread.join()
        mgn_thread.join() 

