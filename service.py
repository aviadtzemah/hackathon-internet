import pygame
import os.path

WIDTH = 1000
HEIGHT = 500

filepath = os.path.dirname(__file__)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
background = pygame.image.load(os.path.join(filepath, "background.jpg")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
font_name = pygame.font.match_font('arial')


# draw text on screen
def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.Color(color))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_msg_stack(surf, x, y, chat, size, color):
    font = pygame.font.Font(font_name, size)
    chat_box = last_msg(chat)
    curr_y = y
    for msg in chat_box:
        text_surface = font.render(msg, True, pygame.Color(color))
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, curr_y)
        surf.blit(text_surface, text_rect)
        curr_y += 20


def last_msg(chat):
    if len(chat) >= 10:
        return chat[-10:]
    return chat


def concat_char(text, char):
    if len(text) == 250:  # maximum amount of characters in a line
        return text
    elif char == "space":
        text += ' '
    else:
        text += char
    return text


def draw_rect(x, y, height, length):
    outline_rect = pygame.Rect(x, y, length, height)
    pygame.draw.rect(screen, pygame.Color('white'), outline_rect, 2)