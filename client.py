import socket
import struct
from game import Game


class Client:
    """
    This class implements the states of a client:
    state 1 - looking for a server
    state 2 - connecting to a server
    state 3 - game mode
    """

    def __init__(self, team_name):
        self.team_name = team_name
        self.tcp_socket = None

    def find_server(self):
        """
        This function is listening for broadcast offer of server.
        the client figures out the server address by the sourceIP and return the received message and sourceIP.
        """
        UDP_PORT = 13117
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # creating UDP socket
        udp_socket.bind(('', UDP_PORT))  # bind the socket to a specific port
        broadcast_msg, (hostIP, _port) = udp_socket.recvfrom(2048)

        udp_socket.close()  # close the connection of the UDP socket
        return hostIP, broadcast_msg

    def extract_port(self, broadcast_msg):
        """
        The function checks if the received message is legal- the first 4 bytes are 0xfeedbeed
        and the next byte is 0x2.
        if the message legal, return the last 2 bytes (the tcp port). otherwise return -1.
        """

        try:
            unpacked_msg = struct.unpack('lch', broadcast_msg)  # unpacking message in format (long, char, short)
        except struct.error:
            print('failed to unpack message -> illegal message')
            return -1

        if unpacked_msg[0] != 0xfeedbeef:
            print(f'wrong magic cookie - expected to FEED BEEF and not {unpacked_msg[0]}')
            return -1

        if unpacked_msg[1] != 0x2:
            print(f'wrong message type - 0x2 != {unpacked_msg[1]}')
            return -1

        return unpacked_msg[2]

    def connect(self, hostIP, tcp_port):
        """
        This function is trying to connect to server.
        If it succeeds return True. otherwise, False.
        """
        print(f'Received offer from {hostIP}, attempting to connect...')

        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # creating TCP socket
        try:
            tcp_socket.connect((hostIP, tcp_port))
        except socket.error:
            print(f'Failed to connect to server at address {hostIP} and port {tcp_port}')
            return False

        tcp_socket.send(f'{self.team_name}\n'.encode('utf-8'))  # send the team name
        return True

    def play(self):
        """
        The game is starting- the client can insert keys for the duration of 10 seconds.
        """
        welcome_msg = self.tcp_socket.recv(2048)
        print(welcome_msg)  # print the welcome message

        self.tcp_socket.setblocking(False)  # set the socket to non-blocking
        game = Game(self)

        game.run()

        self.tcp_socket.close()
        print('Server disconnected, listening for offer requests...')


if __name__ == "__main__":

    print('Client started, listening for offer requests...')

    while True:
        client = Client(team_name='Ribon_Ha_Olamim')
        host, msg = client.find_server()
        port = client.extract_port(msg)

        if port != -1:
            is_connected = client.connect(host, port)

            if is_connected:
                client.play()
