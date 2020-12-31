import time
from socket import *
import threading
import random
import struct
import scapy.all as scapy

class Match:

    """
    constructor parameters:
    queueing_duration - how long are we going to wait for clients to connect
    match_duration - how long the match will be
    broadcast_port - on what port are we going to broadcast the invitations for the match
    tcp_socket - the tcp socket of the server

    connected_clients - info about the connected clients

    group_one_score - the score of group one
    group_two_score - the score of group two
   
    waiting_for_connections - determines if we still accept new clients
    mid_match - determins if we are currently mid game
    """

    def __init__(self, queueing_duration, match_duration, broadcast_port, tcp_socket):
        self.queueing_duration = queueing_duration
        self.match_duration = match_duration
        self.broadcast_port = broadcast_port
        self.tcp_socket = tcp_socket

        self.connected_clients = []

        self.group_one_score = 0
        self.group_two_score = 0

        self.waiting_for_connections = True
        self.mid_match = False

    # the main flow of the match
    def start_match(self):
        self.configure_accept_thread()
        self.wait_for_clients()
        self.start_game()
        self.post_game()

    # setting up the tcp connection of the server
    def configure_accept_thread(self):
        threading.Thread(target=self.connect_clients, args=()).start()

    def connect_clients(self):

        num_of_connected_clients = 0

        while self.waiting_for_connections:
            try:
                client_socket, client_address = self.tcp_socket.accept()  # accepting a new client
                client_socket.settimeout(1) # setting a timeout on the clients' sockets or else their theard wouldn't terminate when the match ends
                num_of_connected_clients += 1
                print("accepted connection from {0}".format(client_address))

                # i am assuming they will send the name and only the name
                name_of_the_client = client_socket.recv(RECIEVE_BUFFER_SIZE).decode('utf-8')

                if not name_of_the_client:  # in case something happened and the client was lost, close the connection
                    num_of_connected_clients -= 1
                    client_socket.close()
                else:  # else add the client to the list of connected clients
                    random_numer = random.randint(0, 100)

                    print(random_numer)

                    # info about each client is saved as follows:
                    # (<the client's index>, <the client's name>, <the client's socket>, <the client's address>, <the group the client's is assigned to>)
                    self.connected_clients.append(
                        [num_of_connected_clients-1, name_of_the_client, client_socket, client_address, (random_numer % 2) + 1])
            except timeout:
                pass

    # broadcasting invitations and waiting for clients to connect for self.queueing_duaration seconds
    def wait_for_clients(self):

        print("queueing started")
        # setting up the socket and the message to send over the broadcast
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind((address, self.broadcast_port+1))
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        message = b'\xfe\xed\xbe\xef\x02\x08\x1d' # the port is 0x081d which is 2077 in hexa

        # from when we are starting to count self.queueing_duration seconds
        stop_queue_reference_time = time.time()

        # from when we are waiting 1 second to send another broadcast
        send_reference_time = time.time()
        print("sending broadcast")
        udp_socket.sendto(message, ('<broadcast>', self.broadcast_port))

        while time.time() - stop_queue_reference_time < self.queueing_duration:

            if time.time() - send_reference_time > 1: # sending a broadcacst each second
                print("sending broadcast")
                udp_socket.sendto(message, ('<broadcast>', self.broadcast_port))
                send_reference_time = time.time()

        udp_socket.close()

        self.waiting_for_connections = False

    # each client's thread will run on this function
    # and it will manage its connection
    def playing_client(self, index, name, connection, address, group):

        while self.mid_match:
            tmout = False
            try:
                data = connection.recv(RECIEVE_BUFFER_SIZE)
            except timeout:
                tmout = True

            # checking if a timeout occured
            if not tmout:
                if not data:  # in case the client disconnected
                    print("client disconnected")
                    for client in self.connected_clients:
                        if index > client[INDEX]:
                            client[INDEX] -= 1

                    del self.connected_clients[index]
                    connection.close()
                    break

                data_decoded = data.decode('utf-8')

                # checking to which group give the score
                if group == 1:
                    self.group_one_score += len(data_decoded)
                else:
                    self.group_two_score += len(data_decoded)

                # sending the data this user sent to all of the connections

                if group == 1: # if the client is in group 1, his text colour will be blue
                    to_send = '\x1b[' + BLUE + name[:-1] + " typed: " + data_decoded + '\x1b[0m'
                else: # else his colour is red
                    to_send = '\x1b[' + RED + name[:-1] + " typed: " + data_decoded + '\x1b[0m'
                
                for client in self.connected_clients:
                    client[SOCKET].sendall(str.encode(to_send))
        
        print("done")

    def welcoming_message_constructor(self):
        welcoming_message = "Welcome to Keyboard Spamming Battle Royale.\n"

        group_one_memebers = "Group 1:\n==\n"
        group_two_memebers = "Group 2:\n==\n"
        # building the groups strs
        for client in self.connected_clients:
            if client[GROUP] == 1:
                group_one_memebers += client[1]
            else:
                group_two_memebers += client[1]

        return welcoming_message + group_one_memebers + group_two_memebers + "\n Start pressing keys on your keyboard as fast as you can!!\n"

    # starting the match for self.match_duration seconds
    def start_game(self):

        print("match started")
        self.mid_match = True
        
        thread_lst = []
        # sending to each client the welcoming message
        # and then starting the threads of each connected client
        welcoming_message = self.welcoming_message_constructor()
        for client in self.connected_clients:
            client[SOCKET].sendall(str.encode(welcoming_message))
            # saving the instance of the threads 
            t = threading.Thread(target=self.playing_client, args=(
                (client[INDEX], client[NAME], client[SOCKET], client[ADDRESS], client[GROUP])))
            thread_lst.append(t)
            t.start()

        time.sleep(10)

        self.mid_match = False

        # the main threads is waiting for all the playing threads to terminate
        for t in thread_lst:
            t.join()

        print("all terminated")

    def construct_summary_message(self):
        summary_message = "Game over! "

        summary_message += ("Group 1 typed in " +
                            str(self.group_one_score) + ". ")
        summary_message += ("Group 2 typed in " +
                            str(self.group_two_score) + ".\n")

        # checking who's the winner
        if self.group_one_score == self.group_two_score:
            summary_message += "It's a tie!\n"
        elif self.group_one_score > self.group_two_score:
            summary_message += "Group 1 wins!\n==\n"

            for client in self.connected_clients:
                if client[GROUP] == 1:
                    summary_message += client[1]
        else:
            summary_message += "Group 2 wins!\n==\n"

            for client in self.connected_clients:
                if client[GROUP] == 2:
                    summary_message += client[1]

        return summary_message

    # prints post game statistics
    def post_game(self):
        print("match ended")

        summary_message = self.construct_summary_message()

        print("sending summary")

        # sending to every connected client the summary message and closing their connection
        for client in self.connected_clients:
            client[SOCKET].sendall(str.encode(summary_message))
            # all of the other threads should've terminated by now so it would not cause any problem to them
            client[SOCKET].close()

# server arguments
address = scapy.get_if_addr("eth1")
print("Server started, listening on IP address {0}".format(address))

# kind of enums for accessing the connected_clients tuples
INDEX = 0 
NAME = 1
SOCKET = 2
ADDRESS = 3
GROUP = 4

# colors of each group. group 1 is blue, group 2 is red
BLUE = '0;34;40m'
RED = '0;31;40m'

# server general paramerters
past_matches = []  # will save all the instances of the past matches
broadcast_port = 13117  # the port we are going to send the broadcast to
port = 2077
queue_time = 10
match_time = 10
RECIEVE_BUFFER_SIZE = 2048

"""
the main loop of the server.
each loop we are creating a new match, starting it and at the end saving its instace.
"""
tcp_socket_for_server = socket(AF_INET, SOCK_STREAM)
tcp_socket_for_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    tcp_socket_for_server.bind((address, port))
    tcp_socket_for_server.listen()  # listening for incoming clients
    tcp_socket_for_server.settimeout(queue_time)
    
    while True:
        current_match = Match(queue_time, match_time, broadcast_port,
                        tcp_socket_for_server)
        current_match.start_match()
        past_matches.append(current_match)
        print("Game over, sending out offer requests...")
    
except error as e:
    print(f'failed to bind the socket: {str(e)}')
