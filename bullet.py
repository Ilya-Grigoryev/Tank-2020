from pygame import *

MOVE_SPEED = 20
WIDTH = 28
HEIGHT = 14
COLOR = "#FF0000"
ALPHA = 10

bullet_images = ['textures/bullet/bullet_1.png',
                 'textures/bullet/bullet_2.png',
                 'textures/bullet/bullet_3.png',
                 'textures/bullet/bullet_4.png']


class Bullet(sprite.Sprite):
    def __init__(self, x, y, direction, type):
        x, y, self.direction, self.type = x, y, direction, type
        sprite.Sprite.__init__(self)
        self.alpha = ALPHA
        self.img_index = 0
        width = WIDTH

        if self.direction == 'left':
            self.xvel = -MOVE_SPEED
            self.yvel = 0
            delta_x = -(width / 2)
            delta_y = 0
            w, h = WIDTH, HEIGHT
            self.img_index = 3
        elif self.direction == 'right':
            self.xvel = MOVE_SPEED
            self.yvel = 0
            delta_x = (width / 2)
            delta_y = 0
            w, h = WIDTH, HEIGHT
            self.img_index = 1
        elif self.direction == 'up':
            self.xvel = 0
            self.yvel = -MOVE_SPEED
            delta_x = 0
            delta_y = -(width / 2)
            w, h = HEIGHT, WIDTH
            self.img_index = 0
        elif self.direction == 'down':
            self.xvel = 0
            self.yvel = MOVE_SPEED
            delta_x = 0
            delta_y = (width / 2)
            w, h = HEIGHT, WIDTH
            self.img_index = 2

        self.image = Surface((w, h))
        self.image = image.load(bullet_images[self.img_index])
        self.image = transform.scale(self.image, (w, h))
        self.rect = Rect(x - w / 2 + delta_x, y - h / 2 + delta_y, w, h)

    def update(self, platforms):
        self.rect.y += self.yvel
        self.rect.x += self.xvel
        return self.collide(platforms)

    def collide(self, platforms):
        for p in platforms:
            if str(type(p)) == "<class 'tank.OfflineEnemyTank'>":
                continue
            if sprite.collide_rect(self, p):
                return True
