#!/usr/bin/python3
import sys
import os
import pygame
import pygame.gfxdraw
import pygame.locals as pyglocal
# local files
import gamemodel
from background import Background
import const
import player as player_def
import burn as burner
from field import Field
from info import InfoNotification

# ----------------------------------------------------------------
# init pygame
# ----------------------------------------------------------------

# init
pygame.init()

# pygame screen
screen = pygame.display.set_mode(Field.XY)

# title
pygame.display.set_caption(const.GAME_TITLE_TEXT)

# font name
font_file_name = os.path.dirname(__file__) + "/font/JuraMedium.ttf"

# default font (infomation)
infofont = pygame.font.Font(font_file_name, 10)

# default font (normal)
sysfont = pygame.font.Font(font_file_name, 12)

# default font (large)
sysfontlarge = pygame.font.Font(font_file_name, 16)

# default font (title)
sysfonttitle = pygame.font.Font(font_file_name, 25)

# frame rate utility
clock = pygame.time.Clock()

# bunning drawer
burning_drawer = burner.BuriningDrawer()

# starry sky drawer
background = Background(infofont, sysfonttitle, sysfontlarge)

# game model
game = gamemodel.Game()

# player control
control = gamemodel.Control()

# field objects
fobjs = gamemodel.FieldObjects(game)

# player object
player = player_def.Player(game, control, fobjs)
fobjs.player = player

# information notify
info = InfoNotification(sysfont, sysfontlarge)

# # ----------------------------------------------------------------
# # game main routine
# # ----------------------------------------------------------------


def draw_game_all():
    "draw all game field"
    # background
    background.draw_starrysky(screen, game)
    # draw movable objects (enemies, bullets, items)
    for obj in fobjs.withoutplayer:
        if obj.state:
            obj.draw(screen, game)
    # draw player's frame
    player.draw(screen)
    # collision animation
    burning_drawer.draw_burning(screen, fobjs.burnpoints)
    # draw infomations
    info.draw_information(screen, player, game)
    # pygame update screen
    pygame.display.update()


def check_gamestate():
    "judge gameover or decrement player's cow"
    if not game.over and player.hp <= 0:
        if game.cowscore <= 0:
            game.backup_score()
            game.over = True
            return
        game.dec_cow()
        player.reset()


def setup_easy():
    game.inc_cow()
    game.inc_cow()
    player.dualcounter = player_def.Player.GUN_DUALITY_UNIT * 2
    for i in range(2):
        fobjs.enemies[i].state = True


def setup_normal():
    game.inc_cow()
    player.dualcounter = player_def.Player.GUN_DUALITY_UNIT * 2
    for i in range(4):
        fobjs.enemies[i].state = True


def setup_hard():
    game.inc_cow()
    player.dualcounter = player_def.Player.GUN_DUALITY_UNIT
    for i in range(8):
        fobjs.enemies[i].state = True


def setup_extra_hard():
    game.inc_cow()
    player.dualcounter = player_def.Player.GUN_DUALITY_UNIT * 4
    for enemy in fobjs.enemies:
        enemy.state = True

# setup difficulity
setups = [setup_easy, setup_normal, setup_hard, setup_extra_hard]


def boot():
    "restart game"
    # reset all objects
    for obj in fobjs.withoutplayer:
        obj.state = False
    for enemy in fobjs.enemies:
        enemy.reset()
    for obj in [game, player, info]:
        obj.reset()
    # modify parameters for each level
    setups[game.level]()


def catch_keypress(key):
    "mapping keypress to the internal model data"
    # start screen
    if not game.start:
        if key == pygame.K_RETURN:
            game.start = True
            boot()
        if key == pygame.K_LEFT:
            game.down_level()
        if key == pygame.K_RIGHT:
            game.up_level()
        return
    # game over screen
    if game.over:
        if key == pygame.K_RETURN:
            game.start = False
        return
    # game pause screen
    if game.pause:
        if key == pygame.K_SPACE:
            game.pause = False
            return
        return
    # game playing screen
    if key == pygame.K_SPACE:
        game.pause = True
        return
    # player's move
    if key == pygame.K_LEFT:
        control.move_left()
    if key == pygame.K_RIGHT:
        control.move_right()
    if key == pygame.K_UP:
        control.move_up()
    if key == pygame.K_DOWN:
        control.move_down()
    # player's gun fire
    if key == pygame.K_d:
        control.on_fire = True
    # player's fire missile
    if key == pygame.K_s:
        control.fire_missile = True
    # player's prisoner exchange trial
    if key == pygame.K_a:
        control.fire_alien = True
    # let player's shield on (left alt)
    if (key == pygame.K_RALT) or (key == pygame.K_LALT):
        control.on_shield = True


def catch_events():
    "caatch event"
    for event in pygame.event.get():
        if event.type == pyglocal.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pyglocal.KEYDOWN:
            catch_keypress(event.key)
        elif event.type == pyglocal.KEYUP:
            control.reset()


def start_screen():
    "start screen"
    blink_counter = 0
    while(not game.start):
        # time delay
        clock.tick(100)
        # key events
        catch_events()
        # start screen draw & blink "press enter"
        blink_counter = (blink_counter + 1) % 100
        press_enter_on = blink_counter < 80
        level_text = game.get_level_text()
        background.draw_start_screen(screen, press_enter_on, level_text)
        pygame.display.update()


def game_routine():
    "game screen"
    while(game.start):
        # time delay
        clock.tick(100)
        # model
        if not game.pause:
            fobjs.update()
            player.update()
            player.shield.update(control.on_shield)
            check_gamestate()
        # key events
        catch_events()
        # field draw
        player.move(control.press_add)
        draw_game_all()

# game process
if __name__ == '__main__':
    while(1):
        start_screen()
        game_routine()
