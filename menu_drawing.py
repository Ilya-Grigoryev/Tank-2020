import pygame
class Menu():
    def __init__(self, window):
        self.window = window

    def draw(self):
        self.window.fill((34, 42, 46))
        pygame.draw.rect(self.window, (143, 68, 38), (95, 195, 210, 60))
        pygame.draw.rect(self.window, (143, 68, 38), (495, 195, 210, 60))
        pygame.draw.rect(self.window, (225, 149, 77), (100, 200, 200, 50))  # go to single player mode
        pygame.draw.rect(self.window, (225, 149, 77), (500, 200, 200, 50))  # go to online mode
        font = pygame.font.Font("textures/font.otf", 90)
        font2 = pygame.font.Font("textures/font2.ttf", 25)
        font3 = pygame.font.Font("textures/font3.ttf", 35)
        text = font.render("TANK 2020", True, (225, 149, 77))   #easy tanks advert
        self.window.blit(text, text.get_rect(center=(400, 70)))
        single_mode_text = font2.render("Single_mode", True, (0, 0, 0))
        self.window.blit(single_mode_text, single_mode_text.get_rect(center=(200, 225)))
        online_mode_text = font2.render("Online_mode", True, (0, 0, 0))
        self.window.blit(online_mode_text, online_mode_text.get_rect(center=(600, 225)))

        wasd_and_arrows = pygame.image.load('textures/wasd_and_arrows.png')
        wasd_and_arrows.set_colorkey((255, 255, 255))
        wasd_and_arrows = pygame.transform.scale(wasd_and_arrows, (200, 80))
        self.window.blit(wasd_and_arrows, wasd_and_arrows.get_rect(center=(267, 410)))
        text = font3.render("moving", True, (139, 153, 168))
        self.window.blit(text, (230, 460))

        space_btn = pygame.image.load('textures/space_btn.png')
        space_btn = pygame.transform.scale(space_btn, (100, 40))
        space_btn.set_colorkey((255, 255, 255))
        self.window.blit(space_btn, space_btn.get_rect(center=(563, 430)))
        text = font3.render("shooting", True, (139, 153, 168))
        self.window.blit(text, (500, 460))
