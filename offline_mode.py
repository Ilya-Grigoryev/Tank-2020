import pygame
import sys
from tank import *
from bullet import *
from blocks import *
import time
import random
from camera import Camera, camera_configure

FPS = 60

WIN_WIDTH = 800
WIN_HEIGHT = 640
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#F2A15A"

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32


def play_offline(my_nick):
    global game_start, game_over, game_result, round_number, opponents_nickname, my_nickname
    my_nickname = my_nick
    map_txt = open('map.txt', 'r')
    level = map_txt.read().split('\n')
    round_number = 1
    map_txt.close()
    total_level_width = int(len(level[0]) / 25 * WIN_WIDTH)
    total_level_height = int(len(level) / 20 * WIN_HEIGHT)

    offlineEnemyTank = OfflineEnemyTank(total_level_width - 128, 96, 100, 'down')
    tank = Tank(96, total_level_height - 128, 4)
    left = right = up = down = False

    game_over = False
    game_start = False
    game_result = 'in game now'

    entities = pygame.sprite.Group()
    platforms = []
    bullets = []
    enemyTanks = []
    enemyTanks.append(offlineEnemyTank)

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Tank 2020")
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))

    bg.fill(Color(BACKGROUND_COLOR))

    def restart():
        tank.deaths += 1
        arr_level = []
        for string in level:
            arr_level.append(list(string))
        while True:
            y, x = random.randint(1, len(arr_level) - 2), random.randint(1, len(arr_level[0]) - 2)
            collide_with_enemyTanks = False
            for enemy in enemyTanks:
                if enemy.rect.colliderect(Rect(x * 32, y * 32, 32, 32)):
                    collide_with_enemyTanks = True
                    break
            if not collide_with_enemyTanks and arr_level[y][x] == ' ':
                break
        tank.rect.x, tank.rect.y = x * 32, y * 32
        tank.health = 100
        tank.direction = 'up'
        tank.img_index = 0
        tank.bandolier = 5

    def spawn_new_enemies():
        tank.kills = 0
        arr_level = []
        for string in level:
            arr_level.append(list(string))
        for _ in range(round_number):
            while True:
                y, x = random.randint(1, len(arr_level)-2), random.randint(1, len(arr_level[0])-2)
                if arr_level[y][x] == ' ':
                    break
            offlineEnemyTank = OfflineEnemyTank(x*32, y*32, 100, 'down')
            entities.add(offlineEnemyTank)
            platforms.append(offlineEnemyTank)
            enemyTanks.append(offlineEnemyTank)

    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                entities.add(pf)
                platforms.append(pf)
            else:
                fl = Floor(x, y)
                entities.add(fl)

            x += PLATFORM_WIDTH
        y += PLATFORM_HEIGHT
        x = 0

    total_level_width = len(level[0]) * PLATFORM_WIDTH
    total_level_height = len(level) * PLATFORM_HEIGHT

    camera = Camera(camera_configure, total_level_width, total_level_height)
    infoPanel = InfoPanel(my_nickname, "Computer")

    entities.add(tank)
    entities.add(offlineEnemyTank)
    platforms.append(offlineEnemyTank)

    last_shot = 0
    pause = False

    while not game_over:
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()

            if e.type == KEYDOWN and (e.key == K_LEFT or e.key == K_a or e.key == 1092) and not pause:
                left = True
                right = up = down = False
            if e.type == KEYDOWN and (e.key == K_RIGHT or e.key == K_d or e.key == 1074) and not pause:
                right = True
                left = up = down = False

            if e.type == KEYUP and (e.key == K_RIGHT or e.key == K_d or e.key == 1074):
                right = False
            if e.type == KEYUP and (e.key == K_LEFT or e.key == K_a or e.key == 1092):
                left = False

            if e.type == KEYDOWN and (e.key == K_UP or e.key == K_w or e.key == 1094) and not pause:
                up = True
                left = right = down = False
            if e.type == KEYDOWN and (e.key == K_DOWN or e.key == K_s or e.key == 1099) and not pause:
                down = True
                left = right = up = False

            if e.type == KEYUP and (e.key == K_UP or e.key == K_w or e.key == 1094):
                up = False
            if e.type == KEYUP and (e.key == K_DOWN or e.key == K_s or e.key == 1099):
                down = False

            if e.type == KEYDOWN and (e.key == K_SPACE) and time.time() - last_shot >= 0.1 and tank.bandolier >= 1 and not pause:
                last_shot = time.time()
                blt = Bullet(tank.rect.centerx, tank.rect.centery, tank.direction, 'tank')
                entities.add(blt)
                bullets.append(blt)
                tank.bandolier -= 1

            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return
            if e.type == MOUSEBUTTONDOWN:
                exit_btn = Rect((760, 0), (40, 40))
                pause_btn = Rect((710, 0), (40, 40))
                if exit_btn.collidepoint(mouse.get_pos()):
                    return
                elif pause_btn.collidepoint(mouse.get_pos()):
                    pause = not pause
                elif pause and 210 < e.pos[0] < 580 and 210 < e.pos[1] < 390:
                    pause = False

        if not pause:
            screen.blit(bg, (0, 0))

            tank.update(screen, left, right, up, down, platforms, bullets, entities, round_number)

            for enemyTank in enemyTanks:
                enemyTank.update(tank, enemyTanks, level, bullets, entities, round_number)
                if enemyTank.health <= 0:
                    tank.kills += 1
                    entities.remove_internal(enemyTank)
                    platforms.pop(platforms.index(enemyTank))
                    enemyTanks.pop(enemyTanks.index(enemyTank))
                    if tank.kills == round_number:
                        round_number += 1
                        spawn_new_enemies()

            if tank.health <= 0:
                restart()

            for i, bullet in enumerate(bullets):
                if bullet.update(platforms):
                    bullets.pop(i)
                    entities.remove_internal(bullet)

            camera.update(tank)
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            infoPanel.update(screen, tank.bandolier, f'{tank.kills}/{round_number}',
                             tank.deaths, tank.health, sum(list(map(lambda et: et.health, enemyTanks)))/round_number, round_number)

            pause_img = pygame.image.load('textures/pause_button.svg')
            pause_img.set_colorkey((255, 255, 255))
            pause_img = pygame.transform.scale(pause_img, (40, 40))
            screen.blit(pause_img, pause_img.get_rect(center=(730, 20)))

        else:
            play_btn = pygame.image.load('textures/play_button.png')
            play_btn.set_colorkey((255, 255, 0))
            play_btn = pygame.transform.scale(play_btn, (400, 200))
            screen.blit(play_btn, play_btn.get_rect(center=(400, 300)))

        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    play_offline("Ilya")
