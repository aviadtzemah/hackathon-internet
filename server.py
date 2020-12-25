import enum
import time

class Match:
    
    def __init__(self, queueing_duration, match_duration):
        self.queueing_duration = queueing_duration
        self.match_duration = match_duration
        
    def start_match(self):
        self.__wait_for_clients()
        self.__start_game()
        self.__post_game()
        return
    
    def __wait_for_clients(self):
        print("queueing started")
        reference_time = time.time()
        current_time = time.time()
        while current_time - reference_time < self.queueing_duration:
            #TODO code for waiting

            current_time = time.time()
        
        return
    
    def __start_game(self):
        print("match started")
        reference_time = time.time()
        current_time = time.time()
        while current_time - reference_time < self.match_duration:
            #TODO code for the game

            current_time = time.time()
        
        return
    
    def __post_game(self):
        print("match ended")
        #TODO send post game statistics to all clients 

        return
    

print("Server started, listening on IP address 172.1.0.71 (might need to be more abstract meaning get the ip at runtime)")

past_matches = []

while True:
    current_match = Match(3, 3)
    current_match.start_match()
    past_matches.append(current_match)

   




