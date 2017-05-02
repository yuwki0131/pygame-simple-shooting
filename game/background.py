import random
import pygame
import pygame.gfxdraw
# local files
import const
from const import Colors
from field import Field
# utilities
from imgutil import ImageLoader


class Background:
    """ Background drawer (Start screen)"""

    # title image
    TITLE_IMAGE_SIZE = 256
    # title header
    TITLE_IMAGE_SIZE_XY = (TITLE_IMAGE_SIZE, TITLE_IMAGE_SIZE)
    # title image y position
    TITLE_IMAGE_Y = 100
    # title text y position
    TITLE_TEXT_Y = 50

    # change level y position
    CHANGE_LEVEL_Y = 400

    # press enter y position
    PRESS_ENTER_Y = 440

    # normal star speed
    NORMAL_STAR_SPEED = 0.8

    # number of stars
    NUMBER_OF_STARS = 100

    # credit text position(x)
    CREDITS_TEXT_X = 20
    # credit text position(y)
    CREDITS_TEXT_Y = 470
    # credit text line spacing
    LINE_SPACING = 8

    # change level arrow text
    CHANGE_ARROW_TEXT = "<                >"

    # press enter text
    PRESS_ENTER_TEXT = " - Press Enter - "

    def __init__(self, infofont, titlefont, largefont):
        self.largefont = largefont
        # init start screen
        # create start screen
        ss_surf = pygame.Surface(Field.XY)
        ss_surf.fill(Colors.WHITE)

        # add title image
        title_img = ImageLoader.load_with_trans(
            "titile_img.png", Background.TITLE_IMAGE_SIZE_XY)
        xy = ((Field.x - Background.TITLE_IMAGE_SIZE) / 2,
              Background.TITLE_IMAGE_Y)
        ss_surf.blit(title_img, xy)

        # add title text
        title_text = titlefont.render(const.GAME_TITLE_TEXT,
                                      True, Colors.BLACK)
        sizew, sizeh = titlefont.size(const.GAME_TITLE_TEXT)
        xy = ((Field.x - sizew) / 2, Background.TITLE_TEXT_Y - sizeh)
        ss_surf.blit(title_text, xy)

        # add credit text
        for i, line in enumerate(const.CREDITS_TEXT.split("\n")):
            text = infofont.render(line, True, Colors.BLACK)
            y = Background.CREDITS_TEXT_Y + Background.LINE_SPACING * i
            ss_surf.blit(text, (Background.CREDITS_TEXT_X, y))

        # init change level arrow
        arrow_text = largefont.render(Background.CHANGE_ARROW_TEXT,
                                      True, Colors.BLACK)
        sizew, sizeh = largefont.size(Background.CHANGE_ARROW_TEXT)
        xy = ((Field.x - sizew) / 2, Background.CHANGE_LEVEL_Y - sizeh)
        ss_surf.blit(arrow_text, xy)

        self.start_screen_surf = ss_surf

        # init press enter blinking text
        self.press_enter_message = largefont.render(
            Background.PRESS_ENTER_TEXT, True, Colors.BLACK)
        sizew, sizeh = largefont.size(Background.PRESS_ENTER_TEXT)
        self.press_enter_xy = ((Field.x - sizew) / 2,
                               Background.PRESS_ENTER_Y - sizeh)

        # init game screen background
        gs_surf = pygame.Surface(Field.XY)
        gs_surf.fill(Colors.WHITE)
        max_range = max(Field.x, Field.y) * 2
        diff_max = 75
        variant = (float(diff_max) / float(max_range))
        for i in range(max_range):
            gray = int(254 - diff_max + i * variant)
            color = (gray, gray, gray)
            pygame.draw.circle(gs_surf, color, (0, 0), max_range - i)
        self.game_screen_surf = gs_surf

        # init background stars
        self.stars = [(random.randint(0, Field.x),
                       (random.randint(0, Field.y)))
                      for _ in range(Background.NUMBER_OF_STARS)]

    def draw_starrysky(self, screen, game):  # background
        # screen.fill(Colors.WHITE)
        screen.blit(self.game_screen_surf, (0, 0))
        if game.over:
            speed = Background.NORMAL_STAR_SPEED + 1
        elif game.pause:
            speed = 0
        else:
            speed = Background.NORMAL_STAR_SPEED
        # move star
        for i, (x, y) in enumerate(self.stars):
            self.stars[i] = (x, (y + speed) % Field.y)
        # draw background
        for (x_d, y_d) in self.stars:
            x, y = int(x_d), int(y_d)
            pygame.gfxdraw.line(screen, x - 1, y, x + 1, y, Colors.BLACK)
            pygame.gfxdraw.line(screen, x, y - 1, x, y + 1, Colors.BLACK)

    def draw_start_screen(self, screen, blinking_state, gamelevel):
        screen.blit(self.start_screen_surf, (0, 0))

        # selected game level description
        gamelevel_text = self.largefont.render(gamelevel, True, Colors.BLACK)
        sizew, sizeh = self.largefont.size(gamelevel)
        xy = ((Field.x - sizew) / 2, Background.CHANGE_LEVEL_Y - sizeh)
        screen.blit(gamelevel_text, xy)

        if blinking_state:
            screen.blit(self.press_enter_message, self.press_enter_xy)
