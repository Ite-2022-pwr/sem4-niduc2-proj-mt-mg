import binascii
import struct

class ArqPacket:
    """
    Class representing an ARQ packet. It contains:
    - pck_type: packet type (0 - data; 1 -  management)
    - msg_type: message type (0- data 1 - ACK, 2 - NACK, 3 - SYN, 4 - SYN-ACK, 5 - FIN, 6 - FIN-ACK)
    - seq: sequence number
    - data: data to be sent (bytes)
    - checksum: checksum of the packet


    The checksum is being calculated within the packet itself at the time of creation.
    Once received packet, we can call func to check if checksum is correct.

    """

    def __init__(self, pck_type, msg_type, seq, data, checksum=None):
        self.pck_type = pck_type
        self.msg_type = msg_type
        self.seq = seq
        if (isinstance(data,bytes)):
            self.data = data
        else:
            try:
                self.data = data.encode("utf-8") # If data is not already bytes, try encoding it using utf-8
            except:
                raise ValueError("Data must be either bytes or string")
        if checksum is None:
            self.checksum = binascii.crc32(self.data)
        else:
            self.checksum = checksum

    def __str__(self):
        return f"pck_type: {self.pck_type}, msg_type: {self.msg_type} seq: {self.seq}, data: {self.data}, checksum: {self.checksum}"


    def checkChecksum(self):
        return binascii.crc32(self.getData()) == self.checksum

    def toBytes(self):
        # In order to send it via udp socket, we need to convert it to bytes
        data_len = len(self.data)
        fmt = f'iii{data_len}sI' # Format of the packet
        return struct.pack(fmt, self.pck_type, self.msg_type, self.seq, self.data, self.checksum)


    @classmethod
    def fromBytes(cls, bytes_data):
        expected_size = struct.calcsize('iii{}sI'.format(len(bytes_data)-16))
        if len(bytes_data) != expected_size:
            raise ValueError(f"Invalid bytes_data size. Expected {expected_size}, got {len(bytes_data)}")
        pck_type, msg_type, seq, data, checksum = struct.unpack('iii{}sI'.format(len(bytes_data)-16), bytes_data)
        return cls(pck_type, msg_type, seq, data, checksum)


    def getData(self):
        return self.data.rstrip(b'\00')


    def decodeData(self):
        return self.data.rstrip(b'\00').decode('utf-8')




