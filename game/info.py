import pygame
import pygame.locals as pyglocal
# local files
from const import Colors
from field import Field
# utilities
from rotateutil import rotate
from imgutil import ImageLoader


def get_center_xy(font, text, height_diff):
    "get center position of "
    sizew, sizeh = font.size(text)
    text_x = (Field.x - sizew) / 2
    text_y = (Field.y - sizeh) / 2 + height_diff
    return (text_x, text_y)


class InfoNotification:
    # info header variables

    # header info height
    HEADER_INFO_HEIGHT = 45
    # tailer info height
    TAILER_INFO_HEIGHT = 20

    # gun power status star
    GUN_STAR_POSITION = (15, 15)
    # gun star rotation coefficient
    STAR_ROTATION_COEFFICIENT = 1.2

    # score text info
    # score text posision
    SCORE_INFO_POSITION = (50, 15)
    # score text
    __score_text = None
    # score before
    __score_before = 0

    # item counter info
    # item counter's initial x position
    ITEM_COUNTER_INIT_X = 160
    # item counter's y position
    ITEM_COUNTER_Y = 15
    # item counter's width
    ITEM_COUNTER_WIDTH = 60
    # item counter text posision
    ITEM_COUNTER_TEXT_X = 25
    # alien text
    __alien_text = None
    # alien before
    __alien_before = 0
    # cow text
    __cow_text = None
    # cow before
    __cow_before = 0

    # hp/shield(power status) info
    # power-status bar's x position
    POWER_STATUS_BAR_X = Field.x - 200
    # power-status bar's initial y position
    POWER_STATUS_BAR_INIT_Y = 8
    # power-status bar's initial y position
    POWER_STATUS_AREA_HEIGHT = 20
    # between power-status text and bar
    BETWEEN_STATUS_TEXT_AND_BAR = 80
    # power-status bar's max width
    POWER_STATUS_BAR_WIDTH = 100
    # power-status bar's background height
    POWER_STATUS_BAR_BACKGROUND_HEIGHT = 8
    # power-status bar's foreground height
    POWER_STATUS_BAR_FOREGROUND_HEIGHT = 6
    # hp text
    __hp_text = None
    # hp before
    __hp_before = 0
    # sp text
    __sp_text = None
    # score before
    __sp_before = 0

    # pause info
    # pause message
    PAUSE_MESSAGE = "Pause"
    # pause text
    pause_text = None

    # gameover info
    # gameover text from center
    GAMEOVER_TEXT_FROM_CENTER = -20
    # gameover score from center
    GAMEOVER_SCORE_FROM_CENTER = 20
    # gameover score from center
    GAMEOVER_PRESS_ENTER_FROM_CENTER = 60
    # gameover message
    GAMEOVER_MESSAGE = "Game Over"
    # gameover text
    gameover_text = None

    # gameover press enter message
    PRESS_ENTER_MESSAGE = " Press Enter - go back to the start screen"
    # gameover text
    pressenter_text = None

    # help message
    KEYBIND_HELP = ("Gun: [D]   Missile: [S]    Alien: [A]"
                    "    Shield: [Alt]    Pause: [Space]")
    # help text
    help_text = None

    # star object (for info display)
    star4d = None
    # rect for star rotation
    star4d_rotate = None
    # alien object (for info display)
    alien4d = None
    # cow object (for info display)
    cow4d = None

    def __update_score_text(self, current_score):
        self.__score_before = current_score
        text = "Score: " + str(current_score).rjust(5)
        self.__score_text = self.largefont.render(text, True, Colors.PINK)

    def __update_hp_text(self, hp):
        self.__hp_before = hp
        text = "HP: " + (str(hp) + "/100").rjust(7)
        self.__hp_text = self.font.render(text, True, Colors.WHITE)

    def __update_sp_text(self, sp):
        self.__sp_before = sp
        text = "SP: " + (str(sp) + "/100").rjust(7)
        self.__sp_text = self.font.render(text, True, Colors.WHITE)

    def __update_cow_text(self, cowscore):
        self.__cow_before = cowscore
        text = "×" + str(int(cowscore))
        self.__cow_text = self.largefont.render(text, True, Colors.WHITE)

    def __update_alien_text(self, alienscore):
        self.__alien_before = alienscore
        text = "×" + str(alienscore)
        self.__alien_text = self.largefont.render(text, True, Colors.WHITE)

    def __draw_gunstar(self, screen, counter):
        left, top = self.GUN_STAR_POSITION
        speed = counter ** InfoNotification.STAR_ROTATION_COEFFICIENT
        rotate(screen, self.star4d, self.star4d_rotate, speed, left, top)

    def __draw_alienscore(self, screen, alienscore):
        left, top = self.ITEM_COUNTER_INIT_X, self.ITEM_COUNTER_Y
        screen.blit(self.alien4d, (left, top))
        screen.blit(self.__alien_text, (left + self.ITEM_COUNTER_TEXT_X, top))

    def __draw_cowscore(self, screen, cowscore):
        left = self.ITEM_COUNTER_INIT_X + self.ITEM_COUNTER_WIDTH
        top = self.ITEM_COUNTER_Y
        screen.blit(self.cow4d, (left, top))
        screen.blit(self.__cow_text, (left + self.ITEM_COUNTER_TEXT_X, top))

    def __draw_scoreinfo(self, screen):
        screen.blit(self.__score_text, self.SCORE_INFO_POSITION)

    def __draw_helptext(self, screen):
        y_diff = (Field. y - self.TAILER_INFO_HEIGHT) / 2
        xy = get_center_xy(self.font, self.KEYBIND_HELP, y_diff)
        screen.blit(self.help_text, xy)

    def __draw_hpinfo(self, screen, hp_float):
        left, top = self.POWER_STATUS_BAR_X, self.POWER_STATUS_BAR_INIT_Y
        left_bar = left + self.BETWEEN_STATUS_TEXT_AND_BAR
        hp = int(hp_float)
        # value text
        screen.blit(self.__hp_text, (left, top))
        # base var
        base_bar_arrange = (left_bar, top, self.POWER_STATUS_BAR_WIDTH,
                            self.POWER_STATUS_BAR_BACKGROUND_HEIGHT)
        pygame.draw.rect(screen, Colors.RED, base_bar_arrange)
        # value bar
        if not hp <= 0:
            value_bar_arrange = (left_bar, top, hp - 1,
                                 self.POWER_STATUS_BAR_FOREGROUND_HEIGHT)
            pygame.draw.rect(screen, Colors.GREEN, value_bar_arrange)

    def __draw_shieldinfo(self, screen, sp_float):
        left = self.POWER_STATUS_BAR_X
        top = self.POWER_STATUS_BAR_INIT_Y + self.POWER_STATUS_AREA_HEIGHT
        left_bar = left + self.BETWEEN_STATUS_TEXT_AND_BAR
        sp = int(sp_float)
        # value text
        screen.blit(self.__sp_text, (left, top))
        # base bar
        base_bar_arrange = (left_bar, top, self.POWER_STATUS_BAR_WIDTH,
                            self.POWER_STATUS_BAR_BACKGROUND_HEIGHT)
        pygame.draw.rect(screen, Colors.ORANGE, base_bar_arrange)
        # value bar
        if not sp <= 0:
            value_bar_arrange = (left_bar, top, sp - 1,
                                 self.POWER_STATUS_BAR_FOREGROUND_HEIGHT)
            pygame.draw.rect(screen, Colors.SKYBLUE, value_bar_arrange)

    def __draw_pause(self, screen):
        screen.fill(Colors.GRAY, special_flags=pyglocal.BLEND_SUB)
        sizew, sizeh = self.largefont.size(self.PAUSE_MESSAGE)
        text_position = ((Field.x - sizew) / 2, (Field.y - sizeh) / 2)
        screen.blit(self.pause_text, text_position)

    def __draw_gameover(self, screen, gamescore):
        # blackout
        screen.fill(Colors.GRAY, special_flags=pyglocal.BLEND_SUB)
        # game over message
        xy = get_center_xy(self.largefont, self.GAMEOVER_MESSAGE,
                           self.GAMEOVER_TEXT_FROM_CENTER)
        screen.blit(self.gameover_text, xy)
        # game over message
        xy = get_center_xy(self.largefont, self.PRESS_ENTER_MESSAGE,
                           self.GAMEOVER_PRESS_ENTER_FROM_CENTER)
        screen.blit(self.pressenter_text, xy)
        # game score message
        gamescore = "Score: " + str(gamescore)
        sctext = self.largefont.render(gamescore, True, Colors.WHITE)
        xy = get_center_xy(self.largefont, gamescore,
                           self.GAMEOVER_SCORE_FROM_CENTER)
        screen.blit(sctext, xy)

    def __update(self, game, player):
        # score update
        if self.__score_before != game.score:
            self.__update_score_text(game.score)
        # cow score update
        if self.__cow_before != game.cowscore:
            self.__update_cow_text(game.cowscore)
        # alien score update
        if self.__alien_before != game.alienscore:
            self.__update_alien_text(game.alienscore)
        # hp info update
        hp = int(player.hp)
        if self.__hp_before != hp:
            self.__update_hp_text(hp)
        # shield info update
        sp = int(player.shield.sp)
        if self.__sp_before != sp:
            self.__update_sp_text(sp)

    def draw_information(self, screen, player, game):
        self.__update(game, player)
        # background
        screen.fill(Colors.DARKGRAY,
                    (0, 0, Field.x, self.HEADER_INFO_HEIGHT))
        screen.fill(Colors.DARKGRAY,
                    (0, Field.y - self.TAILER_INFO_HEIGHT, Field.x, Field.y))
        # infomations
        self.__draw_scoreinfo(screen)
        self.__draw_helptext(screen)
        self.__draw_hpinfo(screen, player.hp)
        self.__draw_shieldinfo(screen, player.shield.sp)
        self.__draw_gunstar(screen, player.dualcounter)
        self.__draw_alienscore(screen, game.alienscore)
        self.__draw_cowscore(screen, game.cowscore)
        if game.over:
            self.__draw_gameover(screen, game.lastscore)
        if game.pause:
            self.__draw_pause(screen)

    def reset(self):
        self.__update_score_text(0)
        self.__update_sp_text(0)
        self.__update_hp_text(0)
        self.__update_cow_text(0)
        self.__update_alien_text(0)

    def __init__(self, font, largefont):
        # init font
        self.font = font
        self.largefont = largefont
        # init game text
        self.pause_text = largefont.render(
            self.PAUSE_MESSAGE, True, Colors.WHITE)
        self.gameover_text = largefont.render(
            self.GAMEOVER_MESSAGE, True, Colors.WHITE)
        self.pressenter_text = largefont.render(
            self.PRESS_ENTER_MESSAGE, True, Colors.WHITE)
        self.help_text = font.render(self.KEYBIND_HELP, True, Colors.WHITE)
        # star object (for info display)
        self.star4d = ImageLoader.load_with_trans("star.png", (20, 20))
        self.star4d_rotate = pyglocal.Rect(0, 0, 20, 20)
        # alien object (for info display)
        self.alien4d = ImageLoader.load_with_trans("alien_i.png", (20, 20))
        # cow object (for info display)
        self.cow4d = ImageLoader.load_with_trans("cow_i.png", (20, 20))
        # init info text
        self.reset()
