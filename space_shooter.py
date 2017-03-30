# Based on http://kidscancode.org/
# Background from http://imgur.com/bHiPMju
# Graphics from http://opengameart.org/content/space-shooter-redux
# Art from Kenney.nl
# Music from http://www.bfxr.net/
# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3

import os
import random
from os import path

import pygame
from pygame import Color

# GAME CONSTS
WIDTH = 480
HEIGHT = 600
FPS = 60

# shield bar
BAR_LENGTH = 100
BAR_HEIGHT = 10

N_MOBS = 8
LIVES = 3
SHOOT_DELAY = 250
DOUBLE_GUN_TIME = 5000
HIDE_TIME = 1000
ROTATION_FRAME_RATE = 50
EXPLOSION_FRAME_RATE = 50
POWERUP_PROBABILITY = 0.1

FONT_NAME = pygame.font.match_font('arial')


# CLASSES
class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(Color('black'))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.radius = 21  # radius required for circle collision

        # player speed in X axis
        self.speed_x = 0

        # shield - players power
        self.shield = 100

        # shoot stuff
        # self.shoot_delay = SHOOT_DELAY
        self.last_shoot = pygame.time.get_ticks()

        # player lives
        self.lives = LIVES
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

        # gun powerups
        self.gun_type = 1
        self.double_gun_time = pygame.time.get_ticks()

    def update(self):

        # Gun powerups - timeout for powerups
        if self.gun_type >= 2 and pygame.time.get_ticks() - self.double_gun_time > DOUBLE_GUN_TIME:
            self.gun_type = 1
            self.double_gun_time = pygame.time.get_ticks()

        # player lives - show if hidden after HIDE_TIME period
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > HIDE_TIME:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        # player sprite and controls
        self.speed_x = 0

        # get pressed key
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        elif keystate[pygame.K_RIGHT]:
            self.speed_x = 5

        # shooting
        if keystate[pygame.K_SPACE]:
            self.shoot()

        # update player position
        self.rect.x += self.speed_x

        # check boundaries of the screen
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        """
        Create new bullet and play shoot sound
        """
        now = pygame.time.get_ticks()
        if now - self.last_shoot > SHOOT_DELAY:
            self.last_shoot = now

            # shoot depending on gun_type
            if self.gun_type == 1:
                Bullet(self.rect.centerx, self.rect.top, (all_sprites, bullets))
            elif self.gun_type >= 2:
                Bullet(self.rect.left, self.rect.centery, (all_sprites, bullets))
                Bullet(self.rect.right, self.rect.centery, (all_sprites, bullets))
            shoot_sound.play()

    # gun powerups
    def double_gun(self):
        self.gun_type = 2
        self.double_gun_time = pygame.time.get_ticks()

    # hide player temporarily after die
    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
    def __init__(self, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image_orig = random.choice(meteor_imgs)
        self.image_orig.set_colorkey(Color('black'))
        self.image = self.image_orig
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)  # required for circle collision

        # mob speed & position
        self.speed_x = 0
        self.speed_y = 0
        self.randomize_position_speed()

        # mob rotation
        self.rotation = 0
        self.rotation_speed = int(random.randrange(-8, 8))
        self.last_rotate = pygame.time.get_ticks()

    def update(self):
        self.rotate()

        # update mob's position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # check boundaries
        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.randomize_position_speed()

    def rotate(self):
        """
        Rotate mob every 50 ticks with rot_speed
        """
        now = pygame.time.get_ticks()
        if now - self.last_rotate > ROTATION_FRAME_RATE:
            self.last_rotate = now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            rotated_image = pygame.transform.rotate(self.image_orig, self.rotation)

            old_center = self.rect.center
            self.image = rotated_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def randomize_position_speed(self):
        """
        Generate new mob's position and speed
        """
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speed_x = random.randrange(-3, 3)
        self.speed_y = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.image = bullet_img
        self.image.set_colorkey(Color('black'))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center

        # animation stuff
        self.frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > EXPLOSION_FRAME_RATE:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Powerup(pygame.sprite.Sprite):
    def __init__(self, center, *groups):
        pygame.sprite.Sprite.__init__(self, *groups)
        self.type = random.choice(['shield', 'double_gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(Color('black'))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed_y = 2

    def update(self):
        self.rect.y += self.speed_y
        # kill if it moves off the top of the screen
        if self.rect.top > HEIGHT:
            self.kill()


# FUNCTIONS
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, Color('white'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, shield):
    if shield < 0:
        shield = 0
    fill = (shield / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    fill_color = Color('green')
    if 25 <= shield < 40:
        fill_color = Color('orange')
    elif shield < 25:
        fill_color = Color('red')
    pygame.draw.rect(surf, fill_color, fill_rect)
    pygame.draw.rect(surf, Color('white'), outline_rect, 2)


# display player lives
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


# start screen
def show_start_screen():
    screen.blit(background_img, background_rect)
    draw_text(screen, "PYKOSZ SHOOTER", 60, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    running = True
    while waiting:
        clock.tick(FPS)
        for evnt in pygame.event.get():
            if evnt.type == pygame.QUIT:
                running = False
                waiting = False
            if evnt.type == pygame.KEYUP:
                waiting = False
    return running

# INITIALIZE PYGAME AND CREATE WINDOW
os.environ['SDL_VIDEO_CENTERED'] = '1'  # must be before pygame.init()!
pygame.mixer.pre_init(22050, -16, 2, 512)
pygame.init()
# pygame.mixer.init()  # optional if pre_init was executed

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# path to media directories
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# change default pygame icon
icon = pygame.image.load(path.join(img_dir, 'playerLife1_orange.png'))
pygame.display.set_icon(icon)

# LOAD IMAGES
background_img = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_rect = background_img.get_rect()
player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()

# meteor images
meteor_list = [
    'meteorBrown_big1.png',
    'meteorBrown_big2.png',
    'meteorBrown_med1.png',
    'meteorBrown_med3.png',
    'meteorBrown_small1.png',
    'meteorBrown_small2.png',
    'meteorBrown_tiny1.png']
meteor_imgs = []
for img in meteor_list:
    meteor_imgs.append(pygame.image.load(path.join(img_dir, img)).convert())

# explosion images
explosion_anim = {
    'large': [],
    'small': [],
    'player': []}
for i in range(9):
    file_name = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, file_name)).convert()
    img.set_colorkey(Color('black'))
    img_large = pygame.transform.scale(img, (75, 75))
    explosion_anim['large'].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_anim['small'].append(img_small)
    # player explosion
    file_name = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, file_name)).convert()
    img.set_colorkey(Color('BLACK'))
    explosion_anim['player'].append(img)

# player lives
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(Color('black'))

# powerup images
powerup_images = {
    'shield': pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert(),
    'double_gun': pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()}

# LOAD SOUNDS & MUSIC
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
explosion_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    explosion_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
player_death_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow4.wav'))
double_gun_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow5.wav'))
# background music
pygame.mixer.music.load(path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(loops=-1)  # start playing background music

# SPRITES
# create sprite groups
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# GAME LOOP
score = 0
start_screen = True
running = True
while running:
    # start screen
    if start_screen:
        running = show_start_screen()
        start_screen = False
        all_sprites.empty()
        mobs.empty()
        bullets.empty()
        powerups.empty()
        player = Player(all_sprites)
        for i in range(N_MOBS):
            mob = Mob((all_sprites, mobs))
        score = 0
    else:
        # keep loop running at the right speed
        clock.tick(FPS)

        # PROCESS INPUT (EVENTS)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                running = False

        # UPDATE
        all_sprites.update()

        # check to see if a bullet hit the mob
        mob_bullet_hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in mob_bullet_hits:
            # play random explosion sound
            random.choice(explosion_sounds).play()

            # increase the score
            score += int(1 / hit.radius * 100)

            # generate explosion
            explosion = Explosion(hit.rect.center, 'large', all_sprites)

            # create and add mob to groups
            mob = Mob([all_sprites, mobs])
            # create_add_mob()

            # randomly generate powerup
            if random.random() > 1 - POWERUP_PROBABILITY:
                powerup = Powerup(hit.rect.center, (all_sprites, powerups))

        # check to see if a mob hit the player
        player_mob_hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in player_mob_hits:
            # decrease player shield
            hit_energy = hit.radius / player.rect.width * 100 / 1.2
            player.shield -= hit_energy

            # generate explosion and new mob & add to groups
            explosion = Explosion(hit.rect.center, 'small', all_sprites)
            mob = Mob((all_sprites, mobs))

            # player death
            if player.shield <= 0:
                player_death_sound.play()
                death_explosion = Explosion(player.rect.center, 'player', all_sprites)

                # hide and reset player parameters
                player.hide()
                player.lives -= 1
                player.shield = 100
                player.gun_type = 1

        # check to see if player hit a powerup
        player_powerup_hit = pygame.sprite.spritecollide(player, powerups, True)
        for hit in player_powerup_hit:
            # check powerup type
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)  # random or const
                if player.shield >= 100:
                    player.shield = 100
                shield_sound.play()

            elif hit.type == 'double_gun':
                player.double_gun()
                double_gun_sound.play()

        # game over
        if player.lives == 0 and not death_explosion.alive():
            start_screen = True

        # DRAW / RENDER
        screen.blit(background_img, background_rect)
        all_sprites.draw(screen)

        draw_text(screen, str(score), 15, WIDTH / 2, 10)  # display score
        draw_shield_bar(screen, 5, 5, player.shield)  # display shield bar
        draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)  # display player lives

        # *after* drawing everything, flip the display
        pygame.display.flip()

pygame.quit()
