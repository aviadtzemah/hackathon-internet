from service import *


class Game:
    def __init__(self, client):
        # pygame configuration
        pygame.init()
        pygame.display.set_caption("Keyboard Spamming")
        clock = pygame.time.Clock()
        FPS = 30
        clock.tick(FPS)

        # game fields
        self.client = client
        self.text = ''
        self.text_blocks = []
        self.opponent_text = ''
        self.opponent_text_blocks = []
        self.game_over = False
        self.current_text_height = 75
        self.current_opponent_text_height = 245
        self.start_time = pygame.time.get_ticks()
        self.seconds = 10  # measure countdown

    def event_handler(self):
        self.key_pressed_handler()  # key pressed event handler
        self.timer_handler()  # timer event handler
        self.receive_msg()  # receive message handler

    def key_pressed_handler(self):
        """
        When a key is pressed, the key will be sent to the server.
        """
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:  # the client hit the keyboard
                self.text = concat_char(self.text, pygame.key.name(event.key))
                self.client.tcp_socket.send(f'{pygame.key.name(event.key)}\n'.encode('utf-8'))  # send the character to server

                if len(self.text) == 250:
                    self.current_text_height += 20
                    self.text_blocks.append(self.text)
                    self.text = ''

            # check for closing window
            if event.type == pygame.QUIT:
                self.game_over = True

    def timer_handler(self):
        """
        This function calculte the current timer value and set game_over to true 
        when the countdown finished. 
        """
        self.seconds = 10 - int((pygame.time.get_ticks() - self.start_time) / 1000)
        if self.seconds == 0:
            self.game_over = True

    def receive_msg(self):
        """
        This function receives a message from the server in non-blocking manner.
        if a message received it will be concatenate to the previous messages.
        """
        msg = self.client.tcp_socket.recv(128).decode('utf-8')
        self.opponent_text = concat_char(self.text, msg)

        if len(self.opponent_text) == 250:
            self.current_opponent_text_height += 20
            self.opponent_text_blocks.append(self.text)
            self.opponent_text = ''

    # draw all objects on the screen
    def draw(self):
        if not self.game_over:
            # draw the background
            screen.blit(background, (0, 0))

            # draw headers
            draw_text(screen, f'{self.seconds}', 50, WIDTH - 50, 10, 'red')
            draw_text(screen, f'Battle Royal', 50, WIDTH / 2, 10, 'white')

            # draw rects
            draw_rect(10, 70, 150, 980)
            draw_rect(10, 240, 250, 980)

            # draw text
            draw_text(screen, self.text, 14, WIDTH / 2, self.current_text_height, 'green')
            draw_msg_stack(screen, WIDTH / 2, 75, self.text_blocks, 14, "green")

            draw_text(screen, self.opponent_text, 14, WIDTH / 2, self.current_opponent_text_height, 'red')
            draw_msg_stack(screen, WIDTH / 2, 245, self.opponent_text_blocks, 14, "red")

            # after drawing everything, flip the display
            pygame.display.flip()

    # Main loop
    def run(self):

        while not self.game_over:
            self.event_handler()
            self.draw()

        pygame.quit()
