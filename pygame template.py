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

# INITIALIZE PYGAME AND CREATE WINDOW
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Template")
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()

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
