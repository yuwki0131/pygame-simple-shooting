import math
import random
import pygame
import pygame.gfxdraw
import pygame.locals as pyglocal
# local files
from const import Colors
from field import Field
# utilities
from calcutil import once_in
from calcutil import in_circle
from rotateutil import rotate
from imgutil import ImageLoader


class UFO:
    # enemy's hp limit (TODO : for debug)
    HP_MAX_VALUE = 100
    # radius interval of type 3 bullet
    BULLET_TYPE3_INTERVAL = 15
    # closer distance with other window
    CLOSER_DISTANCE = 40
    # attack range (decision range to attack player)
    ATTACK_RANGE = 48
    # ufo width
    WIDTH = 32
    # ufo eheight 10
    HEIGHT = 10

    # ufo surface (singleton)
    surf = None
    # ufo shield surface (singleton)
    shield_surf = None
    # ufo light surface (singleton)
    light_surf = None

    def __init__(self, field_objects, game):
        self.wait = 1000
        self.speed = 1000
        self.reset()
        self.__reset_exchange()
        self.destx, self.desty = self.x0, self.y0
        self.field_objects = field_objects
        self.game = game
        if not UFO.surf:
            UFO.surf = ImageLoader.load_with_trans("ufo2.png", (48, 48))
        if not UFO.shield_surf:
            UFO.shield_surf = self.__init_shield()
        if not UFO.light_surf:
            UFO.light_surf = self.__init_light()

    # shield color base red
    SHIELD_COLOR_BASE_R = 100
    # shield color base green
    SHIELD_COLOR_BASE_G = 100
    # shield color base blue
    SHIELD_COLOR_BASE_B = 100
    # mergin of surface
    SHIELD_SURF_MERGIN = 5

    def __init_shield(self):
        "init surf for shield"
        surf_size = (UFO.WIDTH * 2 + UFO.SHIELD_SURF_MERGIN,
                     UFO.WIDTH * 2 + UFO.SHIELD_SURF_MERGIN)
        # radius and surface
        r, surf = UFO.WIDTH, pygame.Surface(surf_size)
        for i in range(r):
            color = (UFO.SHIELD_COLOR_BASE_R - (r + i * 2),
                     UFO.SHIELD_COLOR_BASE_G - (r + i * 2),
                     UFO.SHIELD_COLOR_BASE_B - i)
            pygame.gfxdraw.filled_circle(surf, r, r, r - i, color)
        surf.set_colorkey(Colors.WHITE, pyglocal.RLEACCEL)
        return surf

    # ufo light color red base
    LIGHT_BASE_COLOR_RED = 10
    # ufo light color green base
    LIGHT_BASE_COLOR_GREEN = 10
    # ufo light color blue base
    LIGHT_BASE_COLOR_BLUE = 155
    # ufo light surf
    LIGHT_SURF_HALF = 28

    def __init_light(self):
        "init surf for prisoner-exchagne light"
        lmergin = 5
        lighthalf = 28
        topr = 1
        length = 150
        center = lighthalf + lmergin
        surf = pygame.Surface((lighthalf * 2 + lmergin * 2, length))
        surf.fill(Colors.BLACK)
        for i in range(10):
            ls = [(center + topr - i / 8, 0), (center - topr + i / 8, 0),
                  (center - lighthalf + i / 8, length),
                  (center + lighthalf - i / 8, length),
                  (center + topr - i / 8, 0)]
            color = (UFO.LIGHT_BASE_COLOR_RED,
                     UFO.LIGHT_BASE_COLOR_GREEN,
                     UFO.LIGHT_BASE_COLOR_BLUE - i * 10)
            pygame.gfxdraw.filled_polygon(surf, ls, color)
        surf.set_colorkey(Colors.BLACK, pyglocal.RLEACCEL)
        return surf

    def __reset_exchange(self):
        "reset prisioner-exchange params"
        self.exchange = False
        self.exchange_wait = 300

    def reset(self):
        "called when init or reboot"
        self.x0 = Field.modify_x(random.randint(0, Field.x))
        self.y0 = Field.modify_y_of_enemy(random.randint(0, Field.y / 2))
        self.cooldown = 0
        self.current_type3 = 0
        self.hp = UFO.HP_MAX_VALUE
        self.isfreeze = False
        self.rotatecounter = 0
        self.state = False
        self.__reset_exchange()
        self.movefarwait = 0

    def getxy(self):
        return self.x0, self.y0

    def get_damage(self, value):
        if 0 <= self.hp and not self.isfreeze:
            self.hp -= value
        if self.hp <= 0:
            self.isfreeze = True

    def get_action(self, value):
        if value == 0 and not self.isfreeze:
            self.exchange = True

    def __reset_dest(self):
        distance = random.randint(200, 500)
        x = int(math.cos(math.pi * 2 * random.random()) * distance)
        y = int(math.sin(math.pi * 2 * random.random()) * distance)
        self.destx = Field.modify_x(x + self.x0)
        self.desty = Field.modify_y_of_enemy(y + self.y0)
        self.speed = random.randint(100, 200)
        self.wait = random.randint(100, 1000)

    def __fire_type2(self):
        for b in self.field_objects.bullet2_array:
            if not b.state:
                b.reset(self.x0, self.y0)
                self.cooldown = 10
                return

    def __fire_type3(self):
        for b in self.field_objects.bullet3_array:
            if not b.state:
                self.current_type3 += 1
                self.current_type3 %= UFO.BULLET_TYPE3_INTERVAL
                theta = float(self.current_type3) / \
                    float(UFO.BULLET_TYPE3_INTERVAL)
                b.reset(self.x0, self.y0, theta)
                return

    def __shoot_item(self, itemsArray):
        for item in itemsArray:
            if not item.state:
                angle = random.random() % 0.5
                item.reset(self.x0, self.y0, angle)
                return

    def update(self):
        "decide behavior pattern & act"
        # if prisoner exchange mode
        if self.exchange:
            self.__do_prisoner_exchange()
            return
        # if recovery mode ...
        if self.isfreeze:
            self.__do_recovery_action()
            return
        # regular action
        self.__do_regular_action()

    # ufo waiting time maximum ...
    WAITING_TIME_MAX = 1000
    # ufo waiting time minimum ...
    WAITING_TIME_MIN = 500

    def __needs_to_move(self):
        "this ufo requires to move"
        # too long stay
        if UFO.WAITING_TIME_MAX < self.wait:
            return True
        # closing wall
        closing = Field.close_to_wall(self.x0, self.y0)
        return UFO.WAITING_TIME_MIN < self.wait and closing

    def __move(self):
        "move to the destination"
        if self.__needs_to_move():  # set for move somewhere
            self.__reset_dest()
        elif self.__is_closing_another() and self.movefarwait <= 0:
            self.__reset_dest()
            self.movefarwait = 100
        else:  # do nothing
            self.movefarwait = (self.movefarwait - 1) % 100
            self.wait += 1
        self.x0 += (self.destx - self.x0) / self.speed
        self.y0 += (self.desty - self.y0) / self.speed

    def __do_prisoner_exchange(self):
        "action: evacuate a cow (when an ufo gets alien)"
        self.exchange_wait -= 1
        if self.exchange_wait == 150:
            self.__shoot_item(self.field_objects.item_cow_array)
        if self.exchange_wait < 0:
            self.__reset_exchange()
        self.__move()

    def __do_recovery_action(self):
        "action: recovery hp"
        if UFO.HP_MAX_VALUE <= self.hp:
            # recover from recovery mode
            self.isfreeze = False
            return
        if self.isfreeze:
            self.hp += 0.1
            if once_in(800):
                self.__shoot_item(self.field_objects.item_star_array)
                return
            if once_in(1000):
                self.__shoot_item(self.field_objects.item_bolt_array)
                return
            if once_in(1500):
                self.__shoot_item(self.field_objects.item_alien_array)

    def __do_regular_action(self):
        "action: regular"
        self.__move()
        if not self.cooldown < 0:
            self.cooldown -= 1
            return
        # when game over (no attack)
        if self.game.over:
            return
        # type 1 attack (if target in sight)
        if self.__targetinsight() and self.__not_friendfire():
            self.cooldown = random.randint(10, 20)
            if once_in(100):
                self.cooldown = 200
            self.__fire_type2()
            return
        # no attack
        if once_in(2):
            return
        # type 3 attack
        self.__fire_type3()

    def __not_friendfire(self):
        "check the other ufos in the gun line"
        for friend in self.field_objects.enemies:
            if not friend == self:
                x, y, r = friend.x0, friend.y0, friend.WIDTH
                if x - r < self.x0 < x + r and self.y0 < y:
                    return False
        return True

    def __targetinsight(self):
        "check the player in the gun line"
        left = self.x0 - UFO.ATTACK_RANGE
        right = self.x0 + UFO.ATTACK_RANGE
        in_range = left < self.field_objects.player.x < right
        over_the_player = self.y0 < self.field_objects.player.y
        return in_range and over_the_player

    def touch_at(self, x, y):
        "touch with object(x, y)"
        if self.isfreeze:
            return in_circle((self.x0 - x), (self.y0 - y), UFO.WIDTH)
        x_div_a = (self.x0 - x) / UFO.WIDTH
        y_div_b = (self.y0 - y) / UFO.HEIGHT
        return in_circle(x_div_a, y_div_b, 1)

    # ufo hp bar full height
    HP_BAR_HEIGHT = 4
    # ufo hp bar parameter height
    HP_BAR_VALUE_HEIGHT = 3
    # ufo hp bar distance from main body
    HP_BAR_DISTANCE_FROM_BODY = 35
    # ufo hp bar width
    HP_BAR_WIDTH = 40
    # ufo hp bar x position
    HP_BAR_X_POSITION = int(HP_BAR_WIDTH / 2)

    # distance between center and left most
    TO_LEFT = 20
    # distance between center and top most
    TO_TOP = 12
    # distance between center and bottom most
    TO_BOT = 24

    # shield rectangle
    ROTATE_RECT = pyglocal.Rect(0, 0, WIDTH * 2, HEIGHT * 2)

    def draw(self, screen, _):
        # draw hp
        x, y, w, h = int(self.x0), int(self.y0), UFO.WIDTH, UFO.HEIGHT
        # draw hp info
        # hp bar position
        bar_left = x - UFO.HP_BAR_X_POSITION
        bar_top = y - UFO.HP_BAR_DISTANCE_FROM_BODY
        bar_damaged = int(UFO.HP_BAR_WIDTH * self.hp / UFO.HP_MAX_VALUE)
        # hp bar rect
        bar_base = (bar_left, bar_top, UFO.HP_BAR_WIDTH, UFO.HP_BAR_HEIGHT)
        bar_value = (bar_left, bar_top, bar_damaged, UFO.HP_BAR_VALUE_HEIGHT)
        # draw hp bar
        pygame.draw.rect(screen, Colors.PINK, bar_base)
        pygame.draw.rect(screen, Colors.CYAN, bar_value)

        # draw ufo
        if self.exchange:  # exchange mode (shield)
            position = (x - UFO.LIGHT_SURF_HALF, y + UFO.TO_TOP)
            screen.blit(self.light_surf, position,
                        special_flags=pyglocal.BLEND_SUB)
        if not self.isfreeze:  # not freeze mode
            screen.blit(self.surf, (x - UFO.TO_LEFT, y - UFO.TO_BOT))
            return
        if not self.game.pause:
            self.rotatecounter += self.hp / 10  # % 1
        rotate(screen, self.surf, UFO.ROTATE_RECT,
               self.rotatecounter, x - w, y - h)
        self.__draw_shield(screen, x, y)

    def __is_closing_another(self):
        "closing another ufo?"
        for enemy in self.field_objects.enemies:
            if not enemy == self:
                x_dist = enemy.x0 - self.x0
                y_dist = enemy.y0 - self.y0
                return in_circle(x_dist, y_dist, UFO.CLOSER_DISTANCE)
        return False

    def __draw_shield(self, screen, x, y):
        xy = (x - UFO.WIDTH, y - UFO.WIDTH)
        screen.blit(self.shield_surf, xy, special_flags=pyglocal.BLEND_SUB)
