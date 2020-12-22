import socket
import sys
import time
import getch

HOST = '127.0.0.1'   # localhost
TCP_PORT = 55555
TEAM_NAME = 'Ribon_Haolamim'


"""
state 1 - looking for a server
"""
print('Client started, listening for offer requests...')
udp_socket = socket(socket.AF_INET, socket.SOCK_DGRAM)     # creating UDP socket
msg, server_addr = udp_socket.recvfrom(2048)
print(f'Received offer from {server_addr[0]}, attempting to connect...')


"""
state 2 - connecting to a server
"""
tcp_socket = socket(socket.AF_INET, socket.SOCK_STREAM)     # creating TCP socket
try:
    tcp_socket.connect((HOST, TCP_PORT))
except socket.error:
    print(f'Failed to connect to server at address {HOST} and port {TCP_PORT}')
    sys.exit(1)

tcp_socket.send(f'{TEAM_NAME}\n')  # send the team name


"""
state 3 - game mode
"""
msg = tcp_socket.recv(2048)
print(msg)       # print the welcome message

starting_time = time.time()
while time.time() - starting_time <= 10:
    char = getch.getche()  # read single character from the user
    tcp_socket.send(char)  # send the character to server

# not really waiting for the server to disconnect
udp_socket.close()
tcp_socket.close()
print('Server disconnected, listening for offer requests...')
# need to return to the initial state