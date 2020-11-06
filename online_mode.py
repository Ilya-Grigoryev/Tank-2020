import pygame
import sys
from tank import *
from bullet import *
from blocks import *
from camera import Camera, camera_configure
import socket
from threading import Thread
import time

# from network import Network

FPS = 60
SERVER_ADDRESS = '195.133.48.113'
SERVER_PORT = 4444

WIN_WIDTH = 800
WIN_HEIGHT = 640
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = "#676767"

PLATFORM_WIDTH = 32
PLATFORM_HEIGHT = 32

global game_start, game_over, game_result, round_number, opponents_nickname, my_nickname


def play_online(my_nick):
    global game_start, game_over, game_result, round_number, opponents_nickname, my_nickname
    my_nickname = my_nick
    map_txt = open('map.txt', 'r')
    level = map_txt.read().split('\n')
    round_number = 1
    map_txt.close()
    total_level_width = int(len(level[0]) / 25 * WIN_WIDTH)
    total_level_height = int(len(level) / 20 * WIN_HEIGHT)

    enemyTank = EnemyTank(total_level_width - 128, 96, 100, 'down')
    tank = Tank(96, total_level_height - 128, 2)
    left = right = up = down = False

    game_over = False
    game_start = False
    game_result = 'in game now'

    entities = pygame.sprite.Group()
    platforms = []
    bullets = []

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Tank 2020")
    bg = Surface((WIN_WIDTH, WIN_HEIGHT))

    bg.fill(Color(BACKGROUND_COLOR))

    # client = Client()
    # net = Network('localhost')
    #
    # def send_data():
    #     data = str(tank.rect.x) + ":" + str(tank.rect.y)
    #     reply = net.send(data)
    #     return reply

    # client.send_server(enemyTank)

    def restart():
        global round_number
        print('restarting...')
        tank.rect.x = 96
        tank.rect.y = total_level_height - 128
        tank.health = 100
        tank.direction = 'up'
        tank.img_index = 0
        tank.bandolier = 5
        enemyTank.rect.x = total_level_width - 128
        enemyTank.rect.y = 96
        enemyTank.health = 100
        enemyTank.direction = 'down'
        enemyTank.img_index = 2
        print('restarted!')
        round_number += 1

    def listen_server():
        global game_start, game_over, game_result, opponents_nickname
        while not game_over:
            try:
                data = client.recv(255)
            except:
                return
            msg = str(data.decode("utf-8"))
            try:
                if 'bullet' in msg:
                    b_x, b_y, b_d = tuple(msg[msg.index('bullet'):].split('!')[1].split(':'))
                    if b_d == 'up':
                        b_d = 'down'
                    elif b_d == 'down':
                        b_d = 'up'
                    if b_d == 'left':
                        b_d = 'right'
                    elif b_d == 'right':
                        b_d = 'left'
                    blt = Bullet(total_level_width - int(b_x), total_level_height - int(b_y), b_d,
                                 f'enemy{round_number}')
                    entities.add(blt)
                    bullets.append(blt)
                if "cors" in msg:
                    t_x, t_y, t_d = tuple(msg[msg.index('cors'):].split('!')[1].split(':'))
                    enemyTank.update(total_level_width - int(t_x) - 32, total_level_height - int(t_y) - 32, t_d)
                if "health" in msg:
                    enemyTank.health = int(msg[msg.index('health'):].split('!')[1])
                if "WIN" in msg:
                    game_over = True
                    game_result = f'WIN{msg.split("WIN")[1]}'
                    return
                if "LOSE" in msg:
                    game_over = True
                    game_result = f'LOSE{msg.split("LOSE")[1]}'
                    return
                if "kill" in msg:
                    tank.kills += 1
                    restart()
                if "opponent connected" in msg:
                    game_start = True
                    opponents_nickname = msg.split(':')[1]
                if "opponent disconnected" in msg:
                    client.close()
                    game_over = True
                    game_result = 'WIN\nOpponent disconnected'
                    return
            except:
                print("Not recognized: " + msg)
                continue

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_ADDRESS, SERVER_PORT))
    client.send(f'.nick{my_nickname}nick.'.encode('utf-8'))
    listen_thread = Thread(target=listen_server)
    listen_thread.start()

    pygame.font.init()
    font = pygame.font.SysFont('Arial', 40, True)
    txt = font.render("Searching an opponent...", False, (255, 255, 255))

    searching_gif = [f'textures/searching_gif/frame_{i}_delay-0.08s.gif' for i in range(20)]
    gif_time = searching_time = time.time()
    gif_counter = 0
    search_img = pygame.image.load(searching_gif[gif_counter])
    while not game_start:
        for e in pygame.event.get():
            if e.type == QUIT:
                client.send('disconnect'.encode('utf-8'))
                client.close()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                client.send('disconnect'.encode('utf-8'))
                client.close()
                return
        screen.blit(bg, (0, 0))
        screen.blit(txt, txt.get_rect(center=(400, 100)))
        if time.time() - gif_time >= 0.05:
            search_img = pygame.image.load(searching_gif[gif_counter])
            gif_counter += 1
            gif_time = time.time()
            if gif_counter == 20:
                gif_counter = 0
        pygame.draw.rect(screen, (77, 77, 77), (350, 310, 100, 40))
        sec = font.render(str(int(time.time() - searching_time)), False, (103, 103, 103))
        screen.blit(sec, sec.get_rect(center=(400, 335)))
        screen.blit(search_img, search_img.get_rect(center=(400, 400)))
        pygame.display.update()
        # pygame.time.wait(int(1000 / FPS))
        clock.tick(FPS)

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
    infoPanel = InfoPanel(my_nickname, opponents_nickname)

    entities.add(tank)
    entities.add(enemyTank)
    platforms.append(enemyTank)

    last_shot = 0

    while not game_over:
        for e in pygame.event.get():
            if e.type == QUIT:
                client.send('disconnect'.encode('utf-8'))
                client.close()
                sys.exit()

            if e.type == KEYDOWN and (e.key == K_LEFT or e.key == K_a or e.key == 1092):
                left = True
                right = up = down = False
            if e.type == KEYDOWN and (e.key == K_RIGHT or e.key == K_d or e.key == 1074):
                right = True
                left = up = down = False

            if e.type == KEYUP and (e.key == K_RIGHT or e.key == K_d or e.key == 1074):
                right = False
            if e.type == KEYUP and (e.key == K_LEFT or e.key == K_a or e.key == 1092):
                left = False

            if e.type == KEYDOWN and (e.key == K_UP or e.key == K_w or e.key == 1094):
                up = True
                left = right = down = False
            if e.type == KEYDOWN and (e.key == K_DOWN or e.key == K_s or e.key == 1099):
                down = True
                left = right = up = False

            if e.type == KEYUP and (e.key == K_UP or e.key == K_w or e.key == 1094):
                up = False
            if e.type == KEYUP and (e.key == K_DOWN or e.key == K_s or e.key == 1099):
                down = False

            if e.type == KEYDOWN and (e.key == K_SPACE) and time.time() - last_shot >= 0.1 and tank.bandolier >= 1:
                last_shot = time.time()
                blt = Bullet(tank.rect.centerx, tank.rect.centery, tank.direction, 'ally')
                entities.add(blt)
                bullets.append(blt)
                tank.bandolier -= 1
                client.send(f'bullet!{tank.rect.centerx}:{tank.rect.centery}:{tank.direction}!.'.encode("utf-8"))

            if e.type == KEYDOWN and e.key == K_ESCAPE:
                client.send('disconnect'.encode('utf-8'))
                client.close()
                return
            if e.type == MOUSEBUTTONDOWN:
                exit_btn = Rect(760, 0, 40, 40)
                if exit_btn.collidepoint(mouse.get_pos()):
                    client.send('disconnect'.encode('utf-8'))
                    client.close()
                    return

        screen.blit(bg, (0, 0))

        last_tank_health = tank.health
        tank.update(screen, left, right, up, down, platforms, bullets, entities, round_number)
        if tank.health < last_tank_health:
            client.send(f'health!{tank.health}!.'.encode('utf-8'))

        if tank.health <= 0:
            enemyTank.kills += 1
            client.send('kill'.encode('utf-8'))
            restart()

        if up or down or left or right:
            client.send(f'cors!{tank.rect.x}:{tank.rect.y}:{tank.direction}!.'.encode("utf-8"))

        for i, bullet in enumerate(bullets):
            if bullet.update(platforms):
                bullets.pop(i)
                entities.remove_internal(bullet)

        camera.update(tank)
        for e in entities:
            screen.blit(e.image, camera.apply(e))
        infoPanel.update(screen, tank.bandolier, tank.kills, enemyTank.kills, tank.health, enemyTank.health)

        pygame.display.update()
        # pygame.time.wait(int(1000 / FPS))
        clock.tick(FPS)

    txt = font.render(game_result, False, (255, 255, 255))
    font1 = pygame.font.Font("textures/font2.ttf", 50)
    font2 = pygame.font.Font("textures/font.otf", 110)
    esc_font = pygame.font.SysFont('Arial', 20, True)
    esc_text = esc_font.render("Press ESC to close.", False, (255, 255, 255))
    game_over_text = font1.render("_GAME_OVER_", False, (210, 105, 30))

    if "WIN" in game_result:
        win_or_lose_text = font2.render("WIN", False, (101, 211, 110))
        schet_text = font2.render(game_result.replace('WIN', ''), False, (101, 211, 110))
    else:
        win_or_lose_text = font2.render("LOSE", False, (221, 77, 62))
        schet_text = font2.render(game_result.replace('LOSE', ''), False, (221, 77, 62))

    close_game_result_window = False
    while not close_game_result_window:
        for e in pygame.event.get():
            if e.type == QUIT:
                client.send('disconnect'.encode('utf-8'))
                client.close()
                sys.exit()
            if e.type == KEYDOWN and (e.key == K_ESCAPE):
                close_game_result_window = True
        screen.fill((34, 42, 46))
        screen.blit(game_over_text, game_over_text.get_rect(center=(400, 100)))
        screen.blit(esc_text, esc_text.get_rect(center=(400, 560)))
        screen.blit(win_or_lose_text, win_or_lose_text.get_rect(center=(400, 300)))
        screen.blit(schet_text, schet_text.get_rect(center=(400, 400)))
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    play_online("Ilya")
