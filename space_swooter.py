# Pygame template - skeleton for a new pygame project
import pygame
from pygame import Color
import random
import os

# center window position
os.environ['SDL_VIDEO_CENTERED'] = '1'  # must be before pygame.init()!

WIDTH = 480
HEIGHT = 600
FPS = 60

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50,40))
        self.image.fill(Color('green'))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        elif keystate[pygame.K_RIGHT]:
            self.speed_x = 5

        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

class Mob()

# INITIALIZE PYGAME AND CREATE WINDOW
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)


# GAME LOOP
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)

    # PROCESS INPUT (EVENTS)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    # UPDATE
    all_sprites.update()

    # DRAW / RENDER
    screen.fill(Color('black'))
    all_sprites.draw(screen)

    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
