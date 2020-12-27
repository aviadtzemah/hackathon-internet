import time
from socket import *
import threading
import random

class Match:

    INDEX = 0
    NAME = 1
    SOCKET = 2
    ADDRESS = 3
    GROUP = 4

    """
    constructor parameters:

    queueing_duration - how long are we going to wait for clients to connect
    match_duration - how long the match will be
    broadcast_port - on what port are we going to broadcast the invitations for the match
    host - the server ip
    server_port - the server's tcp port connection
    tcp_socket - the tcp socket of the server

    connected_clients - info about the connected clients

    group_one_score - the score of group one
    group_two_score - the score of group two

    waiting_for_connections - determines if we still accept new clients
    mid_match - determins if we are currently mid game

    """
    
    def __init__(self, queueing_duration, match_duration, broadcast_port, host, server_port):
        self.queueing_duration = queueing_duration
        self.match_duration = match_duration
        self.broadcast_port = broadcast_port
        self.host = host
        self.server_port = server_port
        self.tcp_socket = None

        self.connected_clients = []

        self.group_one_score = 0
        self.group_two_score = 0

        self.waiting_for_connections = True
        self.mid_match = False

    #the main flow of the match  
    def start_match(self):
        self.configure_server()
        self.wait_for_clients()
        self.start_game()
        self.post_game()

    # setting up the tcp connection of the server
    def configure_server(self):
        self.tcp_socket = socket.socket(AF_INET, SOCK_STREAM)      

        try: 
            self.tcp_socket.bind((self.host, self.server_port))

            #TODO NOT SURE IF THE THREAD WILL KILL ITSELF ONCE IT'S OUT OF THE FUNCTION
            threading.Thread(target=self.connect_clients, args=()).start() # starting a thread which'll accept incoming clients
        except socket.error as e:
            print(str(e)) #TODO should i do something else?

    def connect_clients(self):
        global self.connected_clients # making it global so all of the other threads will get the modified version

        self.tcp_socket.listen() # listening for incoming clients

        num_of_connected_clients
        while self.wait_for_clients:
            
            client_socket, client_address = self.tcp_socket.accept() # accepting a new client
            num_of_connected_clients += 1
            print("accepted connection from {0}".format(client_address))

            name_of_the_client = client_socket.recv(2048).decode('utf-8') # i am assuming they will send the name and only the name

            if not name_of_the_client: # in case something happened and the client was lost, close the connection
                num_of_connected_clients -=1
                client_socket.close()
            else: # else add the client to the list of connected clients
                random_numer = random.randint(0, 100)

                # info about each client is saved as follows:
                # (<the client's index>, <the client's name>, <the client's socket>, <the client's address>, <the group the client's is assigned to>)
                self.connected_clients.append((num_of_connected_clients, data_from_connected_client, client_socket, client_address, (random_numer % 2) + 1))                  

    # broadcasting invitations and waiting for clients to connect for self.queueing_duaration seconds
    def wait_for_clients(self):
        global self.wait_for_clients # making it global so all of the other threads will get the modified version

        print("queueing started")
        # setting up the socket and the message to send over the broadcast
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        message = bytes([0xfe, 0xed, 0xbe, 0xef, 0x02, 0x08, 0x1d])
        
        stop_queue_reference_time = time.time() # from when we are starting to count self.queueing_duration seconds

        send_reference_time = time.time() # from when we are waiting 1 second to send another broadcast

        print("sending broadcast")
        #udp_socket.sendto(message, ('255.255.255.255', self.broadcast_port))

        while time.time() - stop_queue_reference_time < self.queueing_duration:
            
            if time.time() - send_reference_time > 1:
                print("sending broadcast")
                #udp_socket.sendto(message, ('255.255.255.255', self.broadcast_port))
                send_reference_time = time.time()     
        
        self.wait_for_clients = False

    # each client's thread will run on this function
    # and it will manage its connection
    def playing_client(self, index, name, connection, address, group)
        # making them global so all of the other threads will get the modified version
        global self.group_one_score
        global self.group_two_score
        global self.connected_clients
        
        while self.mid_match:
            data = connection.recv(2048)

            if not data: # in case the client disconnected
                del self.connected_clients[index]
                connection.close()
                break
            
            data_decoded = data.decode('utf-8')

            # checking to which group give the score
            if group == 1:
                self.group_one_score += len(data_decoded)
            else:
                self.group_two_score += len(data_decoded)

            #sending the data this user sent to all of the connections
            to_send = name + " typed: " + data_decoded
            for client in self.connected_clients
                client[SOCKET].sendall(str.encode(to_send))
             
    def welcoming_message_constructor(self):
        welcoming_message = "Welcome to Keyboard Spamming Battle Royale.\n"
        
        group_one_memebers = "Group 1:\n==\n"
        group_one_memebers = "Group 2:\n==\n"
        for client in self.connected_clients:
            if client[GROUP] == 1:
                group_one_memebers += client[1]
            else:
                group_two_memebers += client[1]

        return welcoming_message.append(group_one_memebers).append(group_two_memebers)
        
    # starting the match for self.match_duration seconds
    def start_game(self):
        global self.mid_match # making it global so all of the other threads will get the modified version

        print("match started")
        self.mid_match = True

        # sending to each client the welcoming message
        # and then starting the threads of each connected client
        welcoming_message = self.welcoming_message_constructor()
        for client in self.connected_clients:
            client[SOCKET].sendall(str.encode(welcoming_message))
            threading.Thread(target=self.playing_client, args=((client[INDEX], client[NAME], client[SOCKET], client[ADDRESS], client[GROUP]))).start()

        reference_time = time.time()

        while time.time() - reference_time < self.match_duration:
            #TODO i just need the loop to run... should i just use sleep()?

        self.mid_match = False
    
    def construct_summary_message(self):
        summary_message = "Game over!"

        summary_message += ("Group 1 typed in " + str(self.group_one_score) ".")
        summary_message += ("Group 2 typed in " + str(self.group_two_score) ".\n")

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
        
        summary_message = construct_summary_message()

        print("sending summary")

        # sending to every connected client the summary message and closing their connection
        for client in self.connect_clients:
            client[SOCKET].sendall(str.encode(summary_message))
            client[SOCKET].close() # all of the other threads should've terminated by now so it would not cause any problem to them
    

print("Server started, listening on IP address 172.1.0.71 (might need to be more abstract meaning get the ip at runtime)")

past_matches = [] # will save all the instances of the past matches
broadcast_port = 13117 #the port we are going to send the broadcast to

"""
the main loop of the server.
each loop we are creating a new match, starting it and at the end saving its instace.
"""
while True:
    current_match = Match()# TODO put the args
    current_match.start_match()
    past_matches.append(current_match)
    print("Game over, sending out offer requests...")
   




