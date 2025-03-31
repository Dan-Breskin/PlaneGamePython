import pygame
from pygame import mixer
import random
import pickle
from GeneralFunctions import ImageButton, Button
import threading

pygame.init()
mixer.init()

screen = pygame.display.set_mode((1000, 700))
planes = pygame.sprite.Group()
clock = pygame.time.Clock()
buildings = pygame.sprite.Group()
backgrounds = pygame.sprite.Group()
counters = pygame.sprite.Group()
font = pygame.font.Font('freesansbold.ttf', 50)
my_font = pygame.font.SysFont('cabin', 50)
menu_font = pygame.font.SysFont('cabin', 100)
game = False

try:
    with open('best_score.pkl', 'rb') as f:
        best_score = pickle.load(f)
except FileNotFoundError:
    with open('best_score.pkl', 'wb') as f:
        pickle.dump(0, f)
        best_score = 0


class Music:
    def __init__(self, file, volume, time):
        mixer.music.load(file)
        mixer.music.set_volume(volume)
        self.time = time
        self.running = True

    def play_music(self):
        if self.running:
            mixer.music.play()
            timer = threading.Timer(self.time, self.play_music)
            timer.daemon = True
            timer.start()

    def stop_music(self):
        self.running = False
        mixer.music.stop()
        mixer.quit()


def sound_effect(file, volume):
    sound = mixer.Sound(file)
    sound.set_volume(volume)
    sound.play()


class Plane(pygame.sprite.Sprite):
    def __init__(self, x, y, size, image):
        super().__init__()
        self.original_image = pygame.image.load(image)
        self.original_image = pygame.transform.scale(self.original_image, (int(400 / (170 / size)), int(size)))
        self.original_image = pygame.transform.flip(self.original_image, True, False)
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.size = size
        self.angle_wait_right = 0
        self.angle_wait_left = 0
        self.move_wait = 0
        self.angle = 0
        self.edge_wait = 0
        planes.add(self)

    def update(self, keys):
        if keys[pygame.K_UP]:
            self.angle_wait_right += 1
            if self.angle_wait_right == 1:
                self.angle_wait_right = 0
                self.angle -= 0.8

        if keys[pygame.K_DOWN]:
            self.angle_wait_left += 1
            if self.angle_wait_left == 1:
                self.angle_wait_left = 0
                self.angle += 0.8

        if self.angle > 56:
            self.angle -= 0.8
        elif self.angle < -56:
            self.angle += 0.8
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.move_wait += 1
        if self.move_wait == 2:
            self.move_wait = 0
            if self.angle != 0:
                self.rect.move_ip(0, -int((self.angle + (self.angle / abs(self.angle) * 9)) / 10))
        if self.rect.centery >= 670 + self.angle * 3 and self.angle < 0:
            self.angle += 2
        elif self.rect.centery <= 30 + self.angle * 3 and self.angle > 0:
            self.angle -= 2


class Building(pygame.sprite.Sprite):
    def __init__(self, x, y, size, wait):
        super().__init__()
        self.original_image = pygame.image.load('Images_Sounds/generic_building.png')
        self.original_image = pygame.transform.scale(self.original_image, (int(70 / (138 / size)), int(size)))
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.size = size
        self.original_wait = wait
        self.wait = wait
        self.x = float(x)
        buildings.add(self)

    def update(self):
        global speed
        self.wait -= 1
        if self.wait == 0:
            self.wait = self.original_wait
            self.x -= speed
            self.rect.x = int(self.x)
        if self.rect.x < 0 - (70 / (138 / self.size)):
            self.kill()


def create_building(x, empty, height, wait, distance):
    size = 700 / height
    for i in range(height):
        if i != empty - 1:
            Building(x, i * size, size, wait)
    Counter(x + ((int(70 / (138 / size))) / 2), 1000, wait)
    spawn_point = x + (plane.rect.x - (1000 - distance))
    Spawn(spawn_point, 1000, wait)


class Background(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.image.load('Images_Sounds/background.png').convert()
        self.image = pygame.transform.scale(self.image, (1000, 700))
        self.rect = self.image.get_rect(topleft=(x, 0))
        self.wait = 0
        backgrounds.add(self)

    def update(self):
        self.wait += 1
        if self.wait == 2:
            self.wait = 0
            self.rect.x -= 1.25
        if self.rect.right <= 0:
            self.rect.left = 1000


class Counter(pygame.sprite.Sprite):
    def __init__(self, x, size, wait):
        super().__init__()
        self.original_image = pygame.image.load('Images_Sounds/generic_building.png')
        self.original_image = pygame.transform.scale(self.original_image, (1, int(size)))
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.size = size
        self.wait = 0
        self.original_wait = wait
        self.wait = wait
        self.x = float(x)
        counters.add(self)

    def update(self):
        global points, best_score, speed
        self.wait -= 1
        if self.wait == 0:
            self.wait = self.original_wait
            self.x -= speed
            self.rect.x = int(self.x)
        if self.rect.x < 0 - (70 / (138 / self.size)):
            self.kill()

        if plane.rect.colliderect(self.rect):
            self.kill()
            if points == best_score:
                best_score += 1
            points += 1


class Spawn(pygame.sprite.Sprite):
    def __init__(self, x, size, wait):
        super().__init__()
        self.original_image = pygame.image.load('Images_Sounds/generic_building.png')
        self.original_image = pygame.transform.scale(self.original_image, (1, int(size)))
        self.image = self.original_image

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.size = size
        self.original_wait = wait
        self.wait = wait
        self.x = float(x)
        counters.add(self)

    def update(self):
        global spawn, speed
        self.wait -= 1
        if self.wait == 0:
            self.wait = self.original_wait
            self.x -= speed
            self.rect.x = int(self.x)
        if self.rect.x < 0 - (70 / (138 / self.size)):
            self.kill()

        if plane.rect.colliderect(self.rect):
            self.kill()
            spawn = True
            spawn = True


back1 = Background(0)
back2 = Background(1000)
start_button = ImageButton('Images_Sounds/start_button.png', (500, 350), 200)
closet_button = ImageButton('Images_Sounds/closet_button1.jpg', (500, 600), 800)
plane_button = ImageButton('Images_Sounds/plane.png', (250, 200), 300)

plane_1_button = ImageButton('Images_Sounds/El_Al_Plane.png', (750, 200), 300)
plane_2_button = ImageButton('Images_Sounds/f18_plane.png', (250, 500), 300)
plane_3_button = ImageButton('Images_Sounds/cessna_plane.png', (750, 500), 300)
plane_buttons = [plane_button, plane_1_button, plane_2_button,
                 plane_3_button]
menu_button = Button((170, 80), (0, 0, 0), 'MENU', (255, 255, 255), menu_font)
plane_image = plane_button.image_name

background_music = Music('Images_Sounds/BackgroundMusic1.mp3', 0.3, 100)
background_music.play_music()

menu = True
game = True
closet = False
running = False
while game:
    if menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                game = False
                background_music.stop_music()
            if start_button.press_check(event):
                menu = False
                running = True
            if closet_button.press_check(event):
                menu = False
                closet = True

        screen.fill((255, 255, 255))
        backgrounds.draw(screen)
        closet_button.draw(screen)
        start_button.draw(screen)
        screen.blit(my_font.render(f'best score: {best_score}', False, (0, 0, 0)), (400, 50))
        pygame.display.flip()
        clock.tick(50)

    plane = Plane(200, 240, 30, plane_image)
    spawn = True
    end = False
    last_num = 3
    points = 0
    speed = 2
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game = False
                background_music.stop_music()
        text_surface = font.render(f'{points}', False, (255, 255, 0))
        pressed_keys = pygame.key.get_pressed()
        screen.fill((0, 0, 255))
        backgrounds.update()
        backgrounds.draw(screen)
        planes.draw(screen)
        buildings.draw(screen)
        text_x = (1000 - text_surface.get_width()) // 2
        screen.blit(text_surface, (text_x, 150))
        screen.blit(my_font.render(f'best score: {best_score}', False, (0, 0, 0)), (700, 50))
        planes.update(pressed_keys)
        buildings.update()
        counters.update()
        if pygame.sprite.spritecollideany(plane, buildings):
            running = False
            menu = True
            sound_effect('Images_Sounds/ExplosionSound.mp3', 1)

        if spawn:
            num = random.randint(1, 5)
            create_building(1000, num, 5, 1, 800)
            spawn = False
            speed += 0.1

        pygame.display.flip()
        clock.tick(120)

    plane.kill()
    for i in buildings:
        i.kill()
    for i in counters:
        i.kill()

    if closet:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                closet = False
                game = False
                background_music.stop_music()
            if menu_button.press_check(event):
                menu = True
                closet = False
            for i in plane_buttons:
                if i.press_check(event):
                    plane_image = i.image_name

        screen.fill((255, 255, 255))
        backgrounds.draw(screen)
        menu_button.draw(screen)
        for i in plane_buttons:
            i.draw(screen)
        screen.blit(my_font.render(f'best score: {best_score}', False, (0, 0, 0)), (400, 50))
        pygame.display.flip()
        clock.tick(50)

with open('best_score.pkl', 'wb') as f:
    pickle.dump(best_score, f)


pygame.quit()
