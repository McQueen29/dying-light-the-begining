import sys
import pygame
import os
import PyQt5
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f'Файл с озображением {fullname} отсутствует')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is None:
        image = image.convert_alpha()
    else:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def start_screen():
    text = ["Заставка", "",
            "Правила игры", "Если в правилах несколько строк,", ""
                                                                "то приходится выводить их построчно"]
    fon = pygame.transform.scale(load_image('fon.png'), (800, 600))
    screen.fill(pygame.Color('blue'))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for el in text:
        rendered_line = font.render(el, 1, pygame.Color(200, 255, 200))
        intro_rect = rendered_line.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height + 10
        screen.blit(rendered_line, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(50)


def terminate():
    pygame.quit()
    sys.exit()


class Fon(pygame.sprite.Sprite):
    image = load_image('fon.png')

    def __init__(self):
        super().__init__(all_sprites)
        self.image = Fon.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottom = height


class Player(pygame.sprite.Sprite):
    image_front = load_image('player_front.png')
    image_right = load_image('palyer_right.png')
    image_left = load_image('player_left.png')

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = Player.image_front
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(tile_width * pos_x, tile_height * pos_y)

    def update(self, key):
        if key == pygame.K_UP:
            if self.rect.y > 400:
                self.rect.y -= 25
        elif key == pygame.K_LEFT:
            if self.rect.x > 0:
                self.image = Player.image_left
                self.rect.x -= 25
        elif key == pygame.K_RIGHT:
            if self.rect.x < 750:
                self.image = Player.image_right
                self.rect.x += 25
        elif key == pygame.K_DOWN:
            if self.rect.y < 450:
                self.rect.y += 25


class Bullet(pygame.sprite.Sprite):
    image = load_image('bullet.png')

    def __init__(self):
        super().__init__(bullet_group, all_sprites)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(player.rect.x + 75, player.rect.y + 25)

    def update(self):
        self.rect.x += 5


def load_level(filename):
    filename = 'levels/' + filename
    with open(filename, 'r', encoding='utf-8') as mapfile:
        level_map = [line.strip() for line in mapfile.readlines()]
    max_width = max([len(x) for x in level_map])
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Player(x, y)
                new_player = Player(x, y)
    return new_player, x, y


class Zombie(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(zombie_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.cnt = -1
        if x <= 1:
            self.to = 'right'
        else:
            self.to = 'left'
        self.hp = 3

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def run(self):
        if self.to == 'left':
            self.rect.x -= 1
        else:
            self.rect.x += 1
        if pygame.sprite.spritecollideany(self, bullet_group):
            self.hp -= 1
            if self.hp == 0:
                self.kill()
            x = bullets[self.cnt]
            x.kill()
            self.cnt -= 1



if __name__ == '__main__':
    width = 800
    height = 600
    tile_width = tile_height = 30
    pygame.display.set_caption('minegor')

    running = True

    clock = pygame.time.Clock()
    start_screen()

    player_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    zombie_group = pygame.sprite.Group()

    fon = Fon()

    player, level_x, level_y = generate_level(load_level('level1'))

    zombie = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 770, 380)
    zombie1 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 800, 405)
    zombie2 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 830, 430)
    zombie3 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 860, 455)
    # x = random.choice([1, 750])
    # if x == 750:
    #    zombie = Zombie(load_image("zombie_to_left_2.png"), 6, 1, x, 450)
    # else:
    #    zombie = Zombie(load_image("zombie_to_right.png"), 6, 1, x, 450)
    cnt = -1
    bullets = [0] * 100
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets[cnt] = Bullet()
                    cnt -= 1
                else:
                    player_group.update(event.key)
        player_group.draw(screen)
        all_sprites.draw(screen)
        zombie_group.draw(screen)
        bullet_group.draw(screen)
        bullet_group.update()
        zombie.run()
        zombie1.run()
        zombie2.run()
        zombie3.run()
        zombie_group.update()
        pygame.display.flip()
        clock.tick(20)
    pygame.quit()
