from pygame import *
from bullet import Bullet
import time
import random


WIDTH = 32
HEIGHT = 32
HEALTH = 100
COLOR = "#000000"

red_tank_images = ['textures/red_tank/tank_1.png',
                   'textures/red_tank/tank_2.png',
                   'textures/red_tank/tank_3.png',
                   'textures/red_tank/tank_4.png']

green_tank_images = ['textures/green_tank/tank_1.png',
                     'textures/green_tank/tank_2.png',
                     'textures/green_tank/tank_3.png',
                     'textures/green_tank/tank_4.png']


class Tank(sprite.Sprite):

    def __init__(self, x, y, move_speed):
        sprite.Sprite.__init__(self)
        self.deaths = 0
        self.move_speed = move_speed
        self.xvel = 0
        self.yvel = 0
        self.startX = x
        self.startY = y
        self.image = Surface((WIDTH, HEIGHT))
        self.rect = Rect(x, y, WIDTH, HEIGHT)
        self.health = HEALTH
        self.img_index = 0
        self.direction = 'up'
        self.image = image.load(green_tank_images[self.img_index])
        self.kills = 0
        self.bandolier = 5
        self.kd_time = 0

    def set_image(self, img_index):
        self.image = image.load(green_tank_images[img_index])

    def update(self, screen, left, right, up, down, platforms, bullets, entities, round_number):
        if left and not (right or down or up):
            self.xvel = -self.move_speed
            self.direction = 'left'
            self.img_index = 3
        elif right and not (left or down or up):
            self.xvel = self.move_speed
            self.direction = 'right'
            self.img_index = 1
        elif up and not (right or down or left):
            self.yvel = -self.move_speed
            self.direction = 'up'
            self.img_index = 0
        elif down and not (right or left or up):
            self.yvel = self.move_speed
            self.direction = 'down'
            self.img_index = 2

        if not (left or right):
            self.xvel = 0
        if not (up or down):
            self.yvel = 0

        if self.bandolier < 5 and time.time() - self.kd_time >= 0.1:
            self.bandolier += 0.1
            self.kd_time = time.time()

        self.rect.y += self.yvel
        self.rect.x += self.xvel
        self.set_image(self.img_index)
        self.collide(self.xvel, self.yvel, platforms, bullets, entities, round_number)

    def collide(self, xvel, yvel, platforms, bullets, entities, round_number):
        for p in platforms:
            if sprite.collide_rect(self, p):

                if xvel > 0:
                    self.rect.right = p.rect.left

                if xvel < 0:
                    self.rect.left = p.rect.right

                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.yvel = 0

                if yvel < 0:
                    self.rect.top = p.rect.bottom

        for i, b in enumerate(bullets):
            if sprite.collide_rect(self, b) and f'enemy{round_number}' in b.type:
                self.health -= b.alpha
                bullets.pop(i)
                entities.remove_internal(b)


class EnemyTank(sprite.Sprite):
    def __init__(self, x: int, y: int, health: int, direction: str):
        super().__init__()
        self.position_x = x
        self.position_y = y
        self.health = health
        self.direction = direction
        self.image = Surface((WIDTH, HEIGHT))
        self.rect = Rect(x, y, WIDTH, HEIGHT)
        self.img_index = 2
        self.image = image.load(red_tank_images[self.img_index])
        self.kills = 0

    def update(self, x, y, direction):
        self.rect.x = x
        self.rect.y = y
        self.direction = direction

        if direction == 'up':
            self.img_index = 2
        elif direction == 'right':
            self.img_index = 3
        elif direction == 'down':
            self.img_index = 0
        elif direction == 'left':
            self.img_index = 1
        self.image = image.load(red_tank_images[self.img_index])


def find_way(level):
    maze = level.splitlines()
    r = next(i for i, line in enumerate(maze) if "S" in line)
    c = maze[r].index("S")
    queue = []
    visited = {}
    visited[(r, c)] = (-1, -1)
    queue.append((r, c))
    while len(queue) > 0:
        r, c = queue.pop(0)
        if maze[r][c] == 'F':
            path = []
            while r != -1:
                path.append((r, c))
                r, c = visited[(r, c)]
            path.reverse()
            return path
        for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            new_r = r + dy
            new_c = c + dx
            if (0 <= new_r < len(maze) and
                    0 <= new_c < len(maze[0]) and
                    not (new_r, new_c) in visited and
                    maze[new_r][new_c] != '-'):
                visited[(new_r, new_c)] = (r, c)
                queue.append((new_r, new_c))


class OfflineEnemyTank(EnemyTank):
    def __init__(self, x: int, y: int, health: int, direction: str):
        super().__init__(x, y, health, direction)
        self.last_way_generate_time = 0
        self.cors_arr = []
        self.last_cor_x, self.last_cor_y = x, y-1
        self.last_enemy_shot = 0
        self.enemy_id = str(random.randint(100000, 999999))
        self.last_cor_arr = []

    def get_cors(self, tank, level, otherTanks):
        str_level = []
        for i in range(len(level)):
            str_level.append(level[i])
        for enemy in otherTanks:
            x_index = round(enemy.rect.x / 32)
            y_index = round(enemy.rect.y / 32)
            str_level[y_index] = str_level[y_index][:x_index] + '-' + str_level[y_index][x_index + 1:]
        x_index = round(tank.rect.x / 32)
        y_index = round(tank.rect.y / 32)
        str_level[y_index] = str_level[y_index][:x_index] + 'F' + str_level[y_index][x_index + 1:]
        x_index = round(self.rect.x / 32)
        y_index = round(self.rect.y / 32)
        str_level[y_index] = str_level[y_index][:x_index] + 'S' + str_level[y_index][x_index + 1:]
        str_level = '\n'.join(str_level)
        points_arr = find_way(str_level)
        if not points_arr:
            return
        self.cors_arr = []
        for i in range(1, len(points_arr)):
            if points_arr[i - 1][0] != points_arr[i][0]:
                for delta in range(points_arr[i - 1][0] * 32, points_arr[i][0] * 32,
                                   (points_arr[i][0] - points_arr[i - 1][0]) * 2):
                    self.cors_arr.append((points_arr[i][1] * 32, delta))
            else:
                for delta in range(points_arr[i - 1][1] * 32, points_arr[i][1] * 32,
                                   (points_arr[i][1] - points_arr[i - 1][1]) * 2):
                    self.cors_arr.append((delta, points_arr[i][0] * 32))
        self.cors_arr.append((points_arr[len(points_arr) - 1][1] * 32, points_arr[len(points_arr) - 1][0] * 32))

    def update(self, tank, otherTanks, level, bullets, entities, round_number):
        if time.time() - self.last_enemy_shot >= 1:
            blt = Bullet(self.rect.centerx, self.rect.centery, self.direction, self.enemy_id+f'enemy{round_number}')
            entities.add(blt)
            bullets.append(blt)
            self.last_enemy_shot = time.time()

        if (time.time() - self.last_way_generate_time >= 2 or len(self.cors_arr) == 0) \
            and (self.rect.x % 32 == 0 and self.rect.y % 32 == 0):
            self.get_cors(tank, level, otherTanks)
            self.last_way_generate_time = time.time()

        collision_with_otherTanks = False
        for otherTank in otherTanks:
            if otherTank == self or otherTank == tank:
                continue
            elif otherTank.rect.colliderect(Rect(self.cors_arr[0][0], self.cors_arr[0][1], 32, 32)):
                collision_with_otherTanks = True
                break

        if collision_with_otherTanks and len(self.last_cor_arr) > 0:
            while not(self.cors_arr[0][0] % 32 == 0 and self.cors_arr[0][1] % 32 == 0):
                self.cors_arr.insert(0, self.last_cor_arr.pop(0))
            self.get_cors(tank, level, otherTanks)
            self.last_way_generate_time = time.time()

        elif not tank.rect.colliderect(Rect(self.cors_arr[0][0], self.cors_arr[0][1], 32, 32)):
            self.rect.x = self.cors_arr[0][0]
            self.rect.y = self.cors_arr[0][1]
            if self.rect.x < self.last_cor_x:
                self.img_index = 3
                self.direction = 'left'
            elif self.rect.x > self.last_cor_x:
                self.img_index = 1
                self.direction = 'right'
            elif self.rect.y < self.last_cor_y:
                self.img_index = 0
                self.direction = 'up'
            elif self.rect.y > self.last_cor_y:
                self.img_index = 2
                self.direction = 'down'
            # print(time.time(), self.enemy_id, self.cors_arr[0])
            self.last_cor_arr.insert(0, self.cors_arr[0])
            if len(self.last_cor_arr) > 32:
                self.last_cor_arr.pop()
            self.last_cor_x, self.last_cor_y = self.cors_arr.pop(0)

        else:
            if self.rect.x == self.cors_arr[0][0]:
                if self.rect.y < self.cors_arr[0][1]:
                    self.img_index = 2
                    self.direction = 'down'
                else:
                    self.img_index = 0
                    self.direction = 'up'
            elif self.rect.y == self.cors_arr[0][1]:
                if self.rect.x < self.cors_arr[0][0]:
                    self.img_index = 1
                    self.direction = 'right'
                else:
                    self.img_index = 3
                    self.direction = 'left'

        self.image = image.load(red_tank_images[self.img_index])
        self.collide(entities, bullets)

    def collide(self, entities, bullets):
        for i, b in enumerate(bullets):
            if sprite.collide_rect(self, b):
                if self.enemy_id in b.type:
                    continue
                elif b.type == 'tank':
                    self.health -= b.alpha
                bullets.pop(i)
                entities.remove_internal(b)
