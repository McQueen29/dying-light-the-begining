import os
import sys

import pygame

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


def start_screen(screen):
    fon = pygame.transform.scale(load_image('fon.png'), (800, 600))
    screen.fill(pygame.Color('blue'))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render("PLAY", True, (100, 255, 100))
    text_info = font.render("INFO", True, (100, 255, 100))
    text_x_info = 600
    text_y_info = 500
    text_x = 150
    text_y = 500
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    screen.blit(text_info, (text_x_info, text_y_info))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)

    pygame.draw.rect(screen, (0, 255, 0), (text_x_info - 10, text_y_info - 10,
                                           text_w + 10, text_h + 20), 1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = event.pos
                if text_x <= coords[0] <= text_x + text_w and text_y <= coords[1] <= text_y + text_h:
                    return
                elif text_x_info <= coords[0] <= text_x_info + text_w and text_y_info <= coords[
                    1] <= text_y_info + text_h:
                    font = pygame.font.Font(None, 30)
                    text = [
                        "Правило: не подпускать зомби к себе!",
                        "",
                        "Управление:",
                        "",
                        "пробел - выстрел",
                        "",
                        "стрелочки - премещение",
                        "",
                        "Девелоперы:",
                        "",
                        "Сеня и Женя <3"
                    ]
                    font = pygame.font.Font(None, 30)
                    text_coord = 50
                    for el in text:
                        rendered_line = font.render(el, 1, pygame.Color(255, 255, 255))
                        intro_rect = rendered_line.get_rect()
                        intro_rect.top = text_coord
                        intro_rect.x = 10
                        text_coord += intro_rect.height + 10
                        screen.blit(rendered_line, intro_rect)
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
        self.rect = self.rect.move(tile_height * pos_x - 20, tile_height * pos_y)
        self.kills = 0

    def update(self, key):
        if key == pygame.K_UP:
            if self.rect.y > 400:
                self.rect.y -= 60
        elif key == pygame.K_LEFT:
            if self.rect.x > 0:
                self.image = Player.image_left
                self.rect.x -= 30
        elif key == pygame.K_RIGHT:
            if self.rect.x < 750:
                self.image = Player.image_right
                self.rect.x += 30
        elif key == pygame.K_DOWN:
            if self.rect.y < 500:
                self.rect.y += 60


class Bullet(pygame.sprite.Sprite):
    image = load_image('bullet.png')

    def __init__(self):
        super().__init__(bullet_group, all_sprites)
        self.image = Bullet.image
        self.cnt = 0
        self.rect = self.image.get_rect()
        if player.image == Player.image_left:
            self.to = -1
            self.rect = self.rect.move(player.rect.x, player.rect.y + 25)
        else:
            self.rect = self.rect.move(player.rect.x + 75, player.rect.y + 25)
            self.to = 1

    def update(self):
        if self.rect.x < 800 and self.rect.x > 0:
            self.rect.x += 10 * self.to
        else:
            self.kill()
        if pygame.sprite.spritecollideany(self, zombie_group):
            self.cnt += 1
        if pygame.sprite.spritecollideany(self, zombie_group) and self.cnt == 4:
            self.cnt = 0
            self.kill()


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

        if x <= 1:
            self.to = 'right'
        else:
            self.to = 'left'
        self.hp = 9

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global fl
        global lose_or_win
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.to == 'left':
            self.rect.x -= 1
        else:
            self.rect.x += 1
        if pygame.sprite.spritecollideany(self, bullet_group):
            self.hp -= 1
            if self.hp == 0:
                self.kill()
                player.kills += 1
                if player.kills == 41:
                    fl = False
                    lose_or_win = 'win'
                zombie_group.draw(screen)
        if pygame.sprite.spritecollideany(self, player_group):
            fl = False
            lose_or_win = 'lose'


if __name__ == '__main__':
    width = 800
height = 600
tile_width = tile_height = 30
pygame.display.set_caption('minegor')

running = True

clock = pygame.time.Clock()
start_screen(screen)

player_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()

fon = Fon()

player, level_x, level_y = generate_level(load_level('level1'))
# first_wave
zombie = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 770, 380)
zombie1 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 780, 440)
zombie2 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 800, 500)
zombie3 = Zombie(load_image("zombie_to_right.png"), 6, 1, 0, 380)
zombie4 = Zombie(load_image("zombie_to_right.png"), 6, 1, -14, 440)
zombie5 = Zombie(load_image("zombie_to_right.png"), 6, 1, -25, 500)
# second_wave
zombie6 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 900, 380)
zombie7 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 910, 440)
zombie8 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 950, 500)
zombie9 = Zombie(load_image("zombie_to_right.png"), 6, 1, -142, 380)
zombie10 = Zombie(load_image("zombie_to_right.png"), 6, 1, -120, 440)
zombie11 = Zombie(load_image("zombie_to_right.png"), 6, 1, -180, 500)

zombie12 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 960, 380)
zombie13 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 990, 440)
zombie14 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1000, 500)
zombie15 = Zombie(load_image("zombie_to_right.png"), 6, 1, -200, 380)
zombie16 = Zombie(load_image("zombie_to_right.png"), 6, 1, -220, 440)
zombie17 = Zombie(load_image("zombie_to_right.png"), 6, 1, -250, 500)
# third_wave
zombie18 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1200, 380)
zombie19 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1230, 440)
zombie20 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1200, 500)
zombie21 = Zombie(load_image("zombie_to_right.png"), 6, 1, -400, 380)
zombie22 = Zombie(load_image("zombie_to_right.png"), 6, 1, -380, 440)
zombie23 = Zombie(load_image("zombie_to_right.png"), 6, 1, -400, 500)

zombie24 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1300, 380)
zombie25 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1330, 440)
zombie26 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1300, 500)
zombie27 = Zombie(load_image("zombie_to_right.png"), 6, 1, -500, 380)
zombie28 = Zombie(load_image("zombie_to_right.png"), 6, 1, -520, 440)
zombie29 = Zombie(load_image("zombie_to_right.png"), 6, 1, -500, 500)

zombie30 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1400, 380)
zombie31 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1430, 440)
zombie32 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1400, 500)
zombie33 = Zombie(load_image("zombie_to_right.png"), 6, 1, -600, 380)
zombie34 = Zombie(load_image("zombie_to_right.png"), 6, 1, -620, 440)
zombie35 = Zombie(load_image("zombie_to_right.png"), 6, 1, -600, 500)

zombie36 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1500, 380)
zombie37 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1530, 440)
zombie38 = Zombie(load_image("zombie_to_left_2.png"), 6, 1, 1500, 500)
zombie39 = Zombie(load_image("zombie_to_right.png"), 6, 1, -730, 380)
zombie40 = Zombie(load_image("zombie_to_right.png"), 6, 1, -750, 440)
zombie41 = Zombie(load_image("zombie_to_right.png"), 6, 1, -730, 500)

cnt = -1
cnt_for_bullets = -1
bullets = [0] * 1000
fl = True
lose_or_win = None
while running:
    if fl:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if player.image != Player.image_front:
                        bullets[cnt] = (Bullet(), player.rect.y)
                        cnt -= 1
                else:
                    player_group.update(event.key)
        player_group.draw(screen)
        all_sprites.draw(screen)
        zombie_group.draw(screen)
        bullet_group.draw(screen)
        bullet_group.update()
        zombie_group.update()
        pygame.display.flip()
        clock.tick(30)
    else:

        pygame.quit()
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            font = pygame.font.Font(None, 30)
            screen.fill('#000000')
            if lose_or_win == 'lose':
                color = (255, 0, 0)
                text = font.render("LOL YOU DIED, RESTART THE GAME", True, (255, 0, 0))
            else:
                color = (0, 0, 255)
                text = font.render("POG YOU WIN, RESTART THE GAME", True, (0, 0, 255))
            text_x = 200
            text_y = 300
            text_w = text.get_width()
            text_h = text.get_height()
            screen.blit(text, (text_x, text_y))
            pygame.draw.rect(screen, color, (text_x - 10, text_y - 10,
                                                   text_w + 20, text_h + 20), 1)
            pygame.display.flip()

pygame.quit()
