import pygame
from player import Player
from enemy import Enemy
from pygame import mixer
from random import choice, randint

# on github: https://github.com/mairongui3/retro_hero.git

# init game, font and music
pygame.init()
pygame.font.init()
mixer.init()

# screen config
width, height = 1024, 720
screen = pygame.display.set_mode((width, height))
pygame_icon = pygame.image.load('assets/image/icon/icon.ico')
pygame.display.set_caption('Retro Hero')
pygame.display.set_icon(pygame_icon)

# frame rate
clock = pygame.time.Clock()
FPS = 60

# define colours
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
PURPLE = (197, 162, 255)
MAGENTA = (149, 86, 255)
YELLOW = (255, 255, 0)

# background image
bg = pygame.image.load('assets/image/background/bg.png').convert_alpha()
bg = pygame.transform.scale(bg, (width, height))

# # extra life image
extra_life = pygame.image.load('assets/image/background/props/health/heart.png').convert_alpha()
extra_life_rect = extra_life.get_rect()

# game over image
game_over_img = pygame.image.load('assets/image/background/props/game-over/game-over.png').convert_alpha()

# background music
mixer.music.load('assets/audio/bg.mp3')
mixer.music.set_volume(0.5)
mixer.music.play(-1, 0.0, 6000)  # fade

# player attack fx
sword_fx = pygame.mixer.Sound("assets/audio/sword.mp3")
sword_fx.set_volume(0.4)

# player death fx
player_death_fx = pygame.mixer.Sound('assets/audio/player_death.mp3')
player_death_fx.set_volume(0.3)

# enemy attack fx
skeleton_attack_fx = pygame.mixer.Sound('assets/audio/skeleton_attack.mp3')
skeleton_attack_fx.set_volume(0.3)

# enemy death fx
death_fx = pygame.mixer.Sound('assets/audio/death.mp3')
death_fx.set_volume(0.3)

# game over fx
game_over_fx = pygame.mixer.Sound('assets/audio/game-over.mp3')
game_over_fx.set_volume(2)

# game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()

# define font
count_font = pygame.font.Font('assets/font/turok.ttf', 100)
score_font = pygame.font.Font('assets/font/turok.ttf', 30)
last_score_font = pygame.font.Font('assets/font/turok.ttf', 25)
pause_font = pygame.font.Font('assets/font/turok.ttf', 72)


# function for drawing background
def draw_bg():
    screen.blit(bg, (0, 0))


# function for drawing text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# score
def save_score(score):
    with open('assets/text/score.txt', 'w') as file:
        file.write(str(score))


def get_score():
    try:
        with open('assets/text/score.txt', 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


score = 0
last_score = get_score()
round_over = False
round_over_time = 0
ROUND_OVER_COOLDOWN = 2500


# load spritesheets
# 100x59
PLAYER_SIZE_X = 100
PLAYER_SIZE_Y = 59
PLAYER_SCALE = 3
PLAYER_OFFSET = [36, 12]
PLAYER_SHEET = pygame.image.load('assets/image/characters/player/player_spritesheet.png').convert_alpha()
PLAYER_DATA = [
    PLAYER_SIZE_X,
    PLAYER_SIZE_Y,
    PLAYER_SCALE,
    PLAYER_OFFSET,
    PLAYER_SHEET,
    sword_fx,
    player_death_fx]

PLAYER_ANIMATION_STEPS = [4, 6, 4, 1, 5, 1, 6]

# 44x52
skeleton_death_count = 0
SKELETON_SIZE_X = 44
SKELETON_SIZE_Y = 52
SKELETON_SCALE = 3
SKELETON_OFFSET = [12, 5]
SKELETON_SHEET = pygame.image.load('assets/image/characters/enemys/skeleton/skeleton_spritesheet.png').convert_alpha()
SKELETON_CLOTHED_SHEET = pygame.image.load('assets/image/characters/enemys/skeleton_clothed'
                                           '/skeleton_clothed_spritesheet.png').convert_alpha()
SKELETON_DATA = [
    SKELETON_SIZE_X,
    SKELETON_SIZE_Y,
    SKELETON_SCALE,
    SKELETON_OFFSET,
    SKELETON_SHEET,
    SKELETON_CLOTHED_SHEET,
    skeleton_attack_fx,
    death_fx]

SKELETON_ANIMATION_STEPS = [6, 8, 6]

player = Player(455, 450, PLAYER_DATA, PLAYER_ANIMATION_STEPS)
enemy = Enemy(1010, 450, SKELETON_DATA, SKELETON_ANIMATION_STEPS)

pause = False
count_pause = 0

extra_life_available = False
x = randint(200, 400)


run = True
while run:
    # frame rate
    clock.tick(FPS)
    # draw background
    draw_bg()

    if not pause:
        # check for player defeat
        if not round_over:
            game_over_fx.stop()
            draw_text('Score: ' + str(score), score_font, MAGENTA, 445, 25)
            draw_text('Last Score: ' + str(last_score), last_score_font, PURPLE, 20, 80)

            if not player.alive:
                save_score(score)
                # display game over image
                screen.blit(game_over_img, (320, height / 3))
                round_over = True
                round_over_time = pygame.time.get_ticks()

            elif not enemy.alive:
                # increase score
                score += 1

                skeleton_death_count += 1
                if skeleton_death_count >= 1 and not extra_life_available:
                    extra_life_available = True

                # spawn new enemy
                x_enemy = choice([2, 1010])
                enemy = Enemy(x_enemy, 450, SKELETON_DATA, SKELETON_ANIMATION_STEPS)

            # extra life
            if skeleton_death_count >= 6:
                extra_life_rect.x = x
                extra_life_rect.y += 3
                if extra_life_rect.y >= 561:
                    extra_life_rect.y = 560

                screen.blit(extra_life, extra_life_rect)
            if extra_life_available and player.rect.colliderect(extra_life_rect):
                extra_life_available = False
                skeleton_death_count = 0
                player.health = 15
                extra_life_rect.y = -3
                x = randint(200, 400)

        else:
            save_score(score)
            last_score = get_score()
            score = 0

            game_over_fx.play()
            pygame.time.wait(ROUND_OVER_COOLDOWN)
            round_over = False
            intro_count = 3

            # spawn player
            player = Player(455, 450, PLAYER_DATA, PLAYER_ANIMATION_STEPS)

            # spawn enemy
            x_enemy = choice([1, 1010])
            enemy = Enemy(x_enemy, 450, SKELETON_DATA, SKELETON_ANIMATION_STEPS)

        # update player
        player.update(screen)
        # draw player
        player.draw(screen)

        # check if game cooldown is equal to 0
        if intro_count <= 0:
            enemy.update()
            enemy.draw(screen)
            enemy.move(player, round_over)
            player.move(width, height, enemy, round_over)

        else:
            draw_text(str(intro_count), count_font, MAGENTA, 500, height / 3)

            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

    else:
        draw_text('Pause', pause_font, YELLOW, 420, height / 2.5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score(score)
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pause = True
                count_pause += 1

                if count_pause == 2:
                    count_pause = 0
                    pause = False

            if event.key == pygame.K_ESCAPE:
                save_score(score)
                run = False

    pygame.display.update()

pygame.quit()
