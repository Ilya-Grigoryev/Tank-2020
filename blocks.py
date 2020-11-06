import pygame

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32
PLATFORM_COLOR = "#808080"


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image = pygame.image.load("textures/Brick_3.png")
        self.rect = pygame.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Floor(Platform):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("textures/floor_1.png")


class InfoPanel:
    def __init__(self, first_player_name, second_player_name):
        self.first_player = {
            'name': first_player_name,
            'kills': 0,
            'health': 100
        }
        self.second_player = {
            'name': second_player_name,
            'kills': 0,
            'health': 100
        }

    def draw_text(self, screen, text, x, y, font_size=20):
        font = pygame.font.SysFont('Arial', font_size, True)
        txt_obj = font.render(text, False, (180, 180, 0))
        screen.blit(txt_obj, txt_obj.get_rect(center=(x, y)))

    def update(self, screen, bandolier, first_player_kills, second_player_kills,
               first_player_health, second_player_health, tanks_count=1):
        self.first_player['kills'] = first_player_kills
        self.second_player['kills'] = second_player_kills
        self.first_player['health'] = first_player_health
        self.second_player['health'] = second_player_health
        self.update_screen(screen, bandolier, tanks_count)

    def update_screen(self, screen, bandolier, tanks_count):
        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(0, 0, 800, 64))
        pygame.draw.line(screen, (0, 0, 0), (400, 0), (400, 64), 4)

        self.draw_text(screen, self.first_player['name'], 150, 30, 25)

        pygame.draw.rect(screen, (0, 180, 0), pygame.Rect(250-20, 20, self.first_player['health'], 30))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(250-20, 20, 100, 30), 3)
        for i in range(1, 10):
            pygame.draw.line(screen, (0, 0, 0), (250-20+i*10, 20), (250-20+i*10, 50), 2)
        self.draw_text(screen, f"{self.first_player['health']}/100", 300-20, 10, 15)

        self.draw_text(screen, str(self.first_player['kills']), 370, 30, 30)
        # ---
        self.draw_text(screen, self.second_player['name'], 650, 30, 25)

        pygame.draw.rect(screen, (0, 180, 0), pygame.Rect(450+20, 20, self.second_player['health'], 30))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(450+20, 20, 100, 30), 3)
        for i in range(1, 10):
            pygame.draw.line(screen, (0, 0, 0), (450+20+i*10, 20), (450+20+i*10, 50), 2)
        self.draw_text(screen, f"{round(self.second_player['health']*tanks_count)}/{100*tanks_count}", 500+20, 10, 15)

        self.draw_text(screen, str(self.second_player['kills']), 430, 30, 30)

        pygame.draw.rect(screen, (255, 128, 0), pygame.Rect(10, 20, bandolier*10, 24))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(10, 20, 50, 24), 3)
        for i in range(1, 5):
            pygame.draw.line(screen, (0, 0, 0), (10 + i * 10, 20), (10 + i * 10, 44), 2)

        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(760, 0, 40, 40))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(760, 0, 40, 40), 2)
        pygame.draw.line(screen, (0, 0, 0), (760, 0), (800, 40), 2)
        pygame.draw.line(screen, (0, 0, 0), (800, 0), (760, 40), 2)
