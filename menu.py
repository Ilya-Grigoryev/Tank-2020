import pygame
from menu_drawing import *
from online_mode import *
from offline_mode import *
import sys


global game_locator


def main():
    global game_locator
    pygame.init()
    pygame.display.set_caption("Tank 2020")
    window = pygame.display.set_mode((800, 640))
    menu = Menu(window)

    font = pygame.font.Font(None, 32)
    input_box = pygame.Rect(300, 130, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    global color, text
    color = color_inactive
    active = False
    text = ''

    while True:
        game_locator = "menu"  # shows game location
        close_window = False
        while not close_window:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 100 < event.pos[0] < 300 and 200 < event.pos[1] < 250:  # to single mode
                        game_locator = "single_mode"
                        close_window = True

                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                        # Change the current color of the input box.
                    color = color_active if active else color_inactive

                    if 500 < event.pos[0] < 700 and 200 < event.pos[1] < 250:  # to online mode
                        if len(text) == 0:
                            color = pygame.Color('red')
                        else:
                            game_locator = "online_mode"
                            close_window = True

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            print(text)
                            text = ''
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        elif not len(text) == 12:
                            text += event.unicode
                        text = text.replace('  ', ' ')

            menu.draw()
            # Render the current text.
            txt_surface = font.render(text, True, color)
            # Resize the box if the text is too long.
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            # Blit the text.
            window.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            # Blit the input_box rect.
            pygame.draw.rect(window, color, input_box, 2)

            pygame.display.update()
            pygame.time.delay(10)

        if game_locator == "online_mode":
                play_online(my_nick=text)

        if game_locator == "single_mode":
                play_offline(my_nick=text)


if __name__ == '__main__':
    main()
