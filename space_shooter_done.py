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


os.environ['SDL_VIDEO_CENTERED'] = '1'  # must be before pygame.init()!

# path to media directories
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

# some game const
WIDTH = 480
HEIGHT = 600
FPS = 60

# shield bar
BAR_LENGTH = 100
BAR_HEIGHT = 10

### Gun powerups
POWERUP_TIME = 5000


def create_add_mob():
    mob = Mob()
    mobs.add(mob)
    all_sprites.add(mob)


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


### Player lives - life counter display
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50,38))
        self.image.set_colorkey(Color('black'))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10

        self.speed_x = 0

        self.radius = 21  # radius required for circle collision
        # pygame.draw.circle(self.image, Color('red'), self.rect.center, self.radius, 1)

        # shield - players power
        self.shield = 100

        # shoot stuff
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()

        ### player's lives
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

        ### Gun powerups
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):

        ### Gun powerups - timeout for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        ### player's lives - unhide if hidden after 1 sec
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
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

        # update player's position
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
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now

            ### Gun powerups
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
            shoot_sound.play()

    ### Gun powerups
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    ### player's lives
    def hide(self):
        # hide the player temporarily
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_imgs)
        self.image_orig.set_colorkey(Color('black'))
        self.image = self.image_orig
        self.rect = self.image.get_rect()

        self.speed_x, self.speed_y = 0, 0

        self.randomize_position()

        self.radius = int(self.rect.width / 2)  # required for circle collision
        # pygame.draw.circle(self.image, Color('red'), self.rect.center, self.radius, 1)

        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_rotate = pygame.time.get_ticks()

    def update(self):
        self.rotate()

        # update mob's position
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.randomize_position()

    def rotate(self):
        """
        Rotate mob every 50 ticks with rot_speed
        """
        now = pygame.time.get_ticks()
        if now - self.last_rotate > 50:
            self.last_rotate = now
            self.rot = (self.rot + self.rot_speed) % 360
            rotated_image = pygame.transform.rotate(self.image_orig, self.rot)

            old_center = self.rect.center
            self.image = rotated_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def randomize_position(self):
        """
        Generate new mob's position and speed
        """
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speed_x = random.randrange(-3, 3)
        self.speed_y = random.randrange(1, 8)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
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
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center

        # animation stuff
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

### Powerups - Power sprite
class Powerup(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
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


# INITIALIZE PYGAME AND CREATE WINDOW
pygame.mixer.pre_init(22050, -16, 2, 512)
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

### change default pygame icon
icon = pygame.image.load(path.join(img_dir, 'playerLife1_orange.png'))
pygame.display.set_icon(icon)

# Score stuff
font_name = pygame.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, Color('white'))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

# load images
background_img = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_rect = background_img.get_rect()
player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
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

explosion_anim = {}
explosion_anim['large'] = []
explosion_anim['small'] = []
### player's explosion
explosion_anim['player'] = []

for i in range(9):
    file_name = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, file_name)).convert()
    img.set_colorkey(Color('black'))
    img_large = pygame.transform.scale(img, (75, 75))
    explosion_anim['large'].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_anim['small'].append(img_small)

    ### player's explosion
    file_name = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, file_name)).convert()
    img.set_colorkey(Color('BLACK'))
    explosion_anim['player'].append(img)

### player's lives
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(Color('black'))

### Powerups images
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

# Sound and music - Load all game sounds
shoot_sound = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
explosion_sounds = []
for snd in ['expl3.wav', 'expl6.wav']:
    explosion_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
pygame.mixer.music.load(path.join(snd_dir, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.4)

### Powerups sounds ###
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow4.wav'))
gun_sound = pygame.mixer.Sound(path.join(snd_dir, 'pow5.wav'))

### Player lives sound ###
player_die_sound = pygame.mixer.Sound(path.join(snd_dir, 'rumble1.ogg'))

# SPRITES - bitmap objects
# create sprite objects and sprite groups
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
###  Powerup
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
for i in range(5):
    create_add_mob()

# GAME LOOP
score = 0
pygame.mixer.music.play(loops=-1)
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)

    # PROCESS INPUT (EVENTS)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         player.shoot()

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
        explosion = Explosion(hit.rect.center, 'large')
        all_sprites.add(explosion)

        # create and add mob to mobs group
        create_add_mob()

        ### Powerup
        if random.random() > 0.9:
            powerup = Powerup(hit.rect.center)
            all_sprites.add(powerup)
            powerups.add(powerup)

    # check to see if a mob hit the player
    player_mob_hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in player_mob_hits:
        hit_energy = hit.radius / player.rect.width * 100 / 1.2
        # print(hit_energy)
        player.shield -= hit_energy

        explosion = Explosion(hit.rect.center, 'small')
        all_sprites.add(explosion)
        create_add_mob()

        if player.shield <= 0:
            ### Playre lives - player's explosion
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)

            ### Playre lives - player's lives
            player.hide()
            player.lives -= 1
            player.shield = 100

            ### Gun powerups
            player.power = 1

    if player.lives == 0 and not death_explosion.alive():
        running = False

    ### Powerups - Colliding with the player
    # check to see if player hit a powerup
    player_powerup_hit = pygame.sprite.spritecollide(player, powerups, True)
    for hit in player_powerup_hit:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)  # random or const
            if player.shield >= 100:
                player.shield = 100
            shield_sound.play()

        if hit.type == 'gun':
            player.powerup()
            gun_sound.play()

    # DRAW / RENDER
    screen.blit(background_img, background_rect)
    all_sprites.draw(screen)

    # shieldbar display
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)

    ### Playre lives - life counter display
    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
