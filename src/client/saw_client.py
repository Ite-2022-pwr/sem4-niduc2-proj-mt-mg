import socket
from shared.ArqPacket import ArqPacket


HOST = "localhost"  # The server's hostname or IP address
PORT = 65432        # Port for data
buffer_size = 16




def handle_packet(data, addr):
    print(f"Received data message: {data.decode()} from {addr}")



if __name__ == "__main__":
    message = "Hello, msg from client that exceeds buffer for sure!".encode()


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
        s.settimeout(1)

        while bytes_sent < len(message):
            tout_count = 0
            print(f"bytes_sent: {bytes_sent}   chunk: {message[bytes_sent:bytes_sent+buffer_size]}")
            chunk = message[bytes_sent:seq*buffer_size]
            packet = ArqPacket(0, 0, seq, chunk).to_bytes()
            s.sendto(packet, (HOST, PORT))
            print(f"Sent {bytes_sent} msg bytes: {chunk}")
            print(f"Packet size: {len(packet)}")
            
            # Wait for ACK
            while True:
                try:
                    data, addr = s.recvfrom(buffer_size)
                    packet = ArqPacket.from_bytes(data)
                    print(f"Received : {packet}")

                    if (packet.msg_type == 1):
                        print(f"Received ACK message: {packet} from {addr}")
                        bytes_sent += len(chunk)
                        seq += 1
                        break
                    elif (packet.msg_type == 2):
                        print(f"Received NACK from {addr}, resending packet seq {packet.seq}")
                        break
                    else:
                        print(f"Received management message: {packet} from {addr}")
                except socket.timeout:
                    print("Timeout")
                    tout_count += 1
                    if (tout_count > 3):
                        print("Too many timeouts, resending packet seq {seq}")
                        
                        break
        


        
        ### END OF TRANSMISION, send FIN msg

        s.sendto(ArqPacket(1, 5, 1, b"FIN").to_bytes(), (HOST, PORT))



