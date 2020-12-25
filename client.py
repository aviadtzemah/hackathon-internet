import socket
import time
import getch

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

    def find_server(self, udp_port):
        """
        This function is listening for broadcast offer of server.
        the client figures out the server address by the sourceIP and returns it.
        """
        print('Client started, listening for offer requests...')
        udp_socket = socket(socket.AF_INET, socket.SOCK_DGRAM)     # creating UDP socket
        udp_socket.bind(('', udp_port))                            # bind the socket to a certain port
        msg, server_addr = udp_socket.recvfrom(2048)
        host = server_addr[0]                                      # figure out the server address by the sourceIP
        print(f'Received offer from {host}, attempting to connect...')

        udp_socket.close()   # close the connection of the UDP socket
        return host

    def connect(self, host, tcp_port):
        """
        This function is trying to connect to server.
        If it succeeds return True. otherwise, False.
        """
        tcp_socket = socket(socket.AF_INET, socket.SOCK_STREAM)     # creating TCP socket
        try:
            tcp_socket.connect((host, tcp_port))
        except socket.error:
            print(f'Failed to connect to server at address {host} and port {tcp_port}')
            return False

        tcp_socket.send(f'{self.team_name}\n')  # send the team name
        return True

    def play(self):
        """
        The game is starting- the client can insert keys for the duration of 10 seconds.
        """
        msg = self.tcp_socket.recv(2048)
        print(msg)       # print the welcome message

        starting_time = time.time()  # starting a timer
        while time.time() - starting_time <= 10:
            char = getch.getche()       # read single character from the user
            self.tcp_socket.send(char)  # send the character to server

        # not really waiting for the server to disconnect
        self.tcp_socket.close()
        print('Server disconnected, listening for offer requests...')


if __name__ == "__main__":

    UDP_PORT = 12345
    TCP_PORT = 23456

    while True:
        client = Client(team_name='Ribon_Haolamim')
        host = client.find_server(UDP_PORT)

        is_connected = client.connect(host, TCP_PORT)
        if not is_connected:
            break

        client.play()
