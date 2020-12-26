import time
from socket import *

class Match:

    """
    constructor parameters:

    queueing_duration - how long are we going to wait for clients to connect
    match_duration - how long the match will be
    broadcast_port - on what port are we going to broadcast the invitations for the match
    host - the server ip
    server_port - the server's tcp port connection
    tcp_socket - the tcp socket of the server
    """
    
    def __init__(self, queueing_duration, match_duration, broadcast_port, host, server_port):
        self.queueing_duration = queueing_duration
        self.match_duration = match_duration
        self.broadcast_port = broadcast_port
        self.host = host
        self.server_port = server_port
        self.tcp_socket = None

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
        except socket.error as e:
            print(str(e)) #TODO should i do something else?

    # broadcasting invitations and waiting for clients to connect for self.queueing_duaration seconds
    def wait_for_clients(self):
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
        
        return
    
    # starting the match for self.match_duration seconds
    def start_game(self):
        print("match started")
        reference_time = time.time()
        current_time = time.time()
        while current_time - reference_time < self.match_duration:
            #TODO code for the game

            current_time = time.time()
        
        return
    
    # prints post game statistics
    def post_game(self):
        print("match ended")
        #TODO send post game statistics to all clients 

        return
    

print("Server started, listening on IP address 172.1.0.71 (might need to be more abstract meaning get the ip at runtime)")

past_matches = [] # will save all the instances of the past matches
broadcast_port = 13117 #the port we are going to send the broadcast to

"""
the main loop of the server.
each loop we are creating a new match, starting it and at the end saving its instace.
"""

current_match = Match(3, 3, broadcast_port)
current_match.start_match()
past_matches.append(current_match)
   




