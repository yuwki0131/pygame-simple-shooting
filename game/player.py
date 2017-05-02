import math
import random
import pygame
import pygame.gfxdraw
import pygame.locals as pyglocal
# local files
import burn as burner
from const import Colors
from field import Field
# utilities
from imgutil import ImageLoader
from calcutil import once_in


class Player:
    """ manage player's airframe(Spaceship) """
    # height of player's airframe
    AIRFRAME_HEIGHT = 60
    # bottom width of player's airframe
    AIRFRAME_BOT_WIDTH = 30
    # move unit
    AIRFRAME_MOVEUNIT = 2
    # TODO : searching ...
    AIRFRAME_HEAD = (8, 0)
    # TODO : searching ...
    AIRFRAME_LEFT = (-15, 60)
    # TODO : searching ...
    AIRFRAME_RIGHT = (31, 60)
    # bullet starting position
    FIRE1_INIT_X = 0
    FIRE1_INIT_Y = 0
    # bullet starting position
    FIRE2_INIT_X = 4
    FIRE2_INIT_Y = 0
    # bullet starting position
    FIRE3_INIT_X = -8
    FIRE3_INIT_Y = 15
    # bullet starting position
    FIRE4_INIT_X = 12
    FIRE4_INIT_Y = 15
    # player's hp limit (TODO : for debug)
    HP_MAX_VALUE = 100

    # the time that gun is duality
    GUN_DUALITY_UNIT = 1000

    # dual attack fire limit 1
    DUAL_FIRE_LIMIT = 0

    # quad attack fire limit 2
    QUAD_FIRE_LIMIT = 2000

    init_x = 0
    init_y = 0

    # surface
    surf = None

    def __init__(self, game, control, field_objects):
        self.init_x = Field.PLAYER_INIT_CENTER_X
        self.init_y = Field.PLAYER_INIT_CENTER_Y
        self.reset()
        self.control = control
        self.game = game
        self.field_objects = field_objects
        if not Player.surf:
            Player.surf = ImageLoader.load_with_trans(
                "spaceship.png", (45, 66))

    def reset(self):
        self.x = self.init_x
        self.y = self.init_y
        self.dualcounter = 0
        self.rotatecounter = 0
        self.holdfire = 0
        self.holdmissile = 0
        self.holdalien = 0
        self.shield = Shield()
        self.hp = self.HP_MAX_VALUE

    def getxy(self):
        return self.x, self.y

    def move(self, xyadd):
        x, y = xyadd
        if Field.x_in_movablerange(self.x + x):
            self.x += x
        if Field.y_in_movablerange(self.y + y):
            self.y += y

    def fire(self):
        self.__launch_bullet(self.x + self.FIRE1_INIT_X,
                             self.y + self.FIRE1_INIT_Y)
        if not Player.DUAL_FIRE_LIMIT < self.dualcounter:
            return
        self.__launch_bullet(self.x + self.FIRE2_INIT_X,
                             self.y + self.FIRE2_INIT_Y)
        if not Player.QUAD_FIRE_LIMIT < self.dualcounter:
            return
        self.__launch_bullet(self.x + self.FIRE3_INIT_X,
                             self.y + self.FIRE3_INIT_Y)
        self.__launch_bullet(self.x + self.FIRE4_INIT_X,
                             self.y + self.FIRE4_INIT_Y)

    def __launch_bullet(self, x, y):
        for b in self.field_objects.bullet1_array:
            if not b.state:
                b.reset(x, y)
                return

    def launch_missile(self):
        for m in self.field_objects.missile_array:
            if not m.state:
                m.reset(self.x, self.y)
                self.find_target(m)
                return

    def launch_alien(self):
        for b in self.field_objects.bullet_alien_array:
            if not b.state:
                b.reset(self.x, self.y)
                return

    def get_dual(self):
        self.dualcounter += Player.GUN_DUALITY_UNIT

    def get_damage(self, damage):
        if 0 < self.hp:
            self.hp += damage
        if self.HP_MAX_VALUE < self.hp:
            self.hp = self.HP_MAX_VALUE

    def find_target(self, missile):
        x, y = self.x, self.y
        dist = Field.FARTHEST
        for enemy in self.field_objects.enemies:
            if enemy:
                ex, ey = enemy.getxy()
                ndist = math.sqrt((ex - x) ** 2 + (ey - y) ** 2)
                if ndist < dist:
                    dist = ndist
                    missile.lockon(enemy)

    def recover_hp10(self):
        self.hp += 10
        if self.HP_MAX_VALUE < self.hp:
            self.hp = self.HP_MAX_VALUE

    def shield_enabled(self):
        return self.control.on_shield and 0 < self.shield.sp

    def update(self):
        if 0 < self.dualcounter:
            self.dualcounter -= 1
        hold = random.randint(1, 25) < self.holdfire
        if self.control.on_fire and hold:
            self.fire()
            self.holdfire = 0
        hold = random.randint(150, 250) < self.holdalien
        if self.control.fire_alien and hold and 0 < self.game.alienscore:
            self.launch_alien()
            self.game.dec_alien()
            self.holdalien = 0
        hold = random.randint(150, 250) < self.holdmissile
        if self.control.fire_missile and hold:
            self.launch_missile()
            self.holdmissile = 0
        self.holdfire += 1
        self.holdalien += 1
        self.holdmissile += 1
        if self.hp < 0:
            self.hp = 0

    def draw(self, screen):
        # lock-on sight
        self.__draw_gun_sight(screen)

        # fire!
        if self.control.on_fire:
            burner.draw_gunburn(screen, self.x + 6, self.y + 6)
            if Player.DUAL_FIRE_LIMIT < self.dualcounter:
                burner.draw_gunburn(screen, self.x + 10, self.y + 6)
            if Player.QUAD_FIRE_LIMIT < self.dualcounter:
                burner.draw_gunburn(screen, self.x - 2, self.y + 21)
                burner.draw_gunburn(screen, self.x + 18, self.y + 21)

        if self.game.over:
            # player's body burining
            if once_in(10):
                burnpoint = (self.x - random.randint(0, 40) + 20,
                             self.y - random.randint(0, 60) + 60)
                self.field_objects.burnpoints.add(
                    (burnpoint, random.randint(10, 40)))

        # draw player
        screen.blit(self.surf, (self.x - self.AIRFRAME_BOT_WIDTH / 2, self.y))

        # draw player's shield
        if self.control.on_shield:
            self.shield.draw(self, screen)

    def __draw_gun_sight(self, screen):
        x, y = int(self.x + 5), int(self.y - 150)
        pygame.gfxdraw.line(screen, x - 5, y, x + 5, y, Colors.RED)
        pygame.gfxdraw.line(screen, x, y - 5, x, y + 5, Colors.RED)


class Shield:
    """ player's shield """
    # shield point max value
    SP_MAX_VALUE = 100
    # shield point consumption
    SP_CONSUME_UNIT = -0.1
    # shield point recovery
    SP_RECOVER_UNIT = 0.1

    # shield radius
    RADIUS = 45
    # shield color base (red)
    SHIFT_RED = 0
    # shield color base (green)
    SHIFT_GREEN = 0
    # shield color base (blue)
    SHIFT_BLUE = 0
    # mergin for surface
    SURFACE_MERGIN = 10
    # shield color variation
    COLOR_VARIATION_SIZE = 100

    def init_surface(self, j):
        size = self.RADIUS * 2 + self.SURFACE_MERGIN
        surf = pygame.Surface((size, size))
        for i in range(self.RADIUS):
            color = (self.SHIFT_RED,
                     self.SHIFT_GREEN + j,
                     self.SHIFT_BLUE + i)
            xy = (self.RADIUS, self.RADIUS + int(i / 2))
            current_radius = int(self.RADIUS - i / 2)
            pygame.draw.circle(surf, color, xy, current_radius)
        surf.set_colorkey(Colors.WHITE, pyglocal.RLEACCEL)
        return surf

    def __init__(self):
        self.sp = self.SP_MAX_VALUE
        self.surf = {}
        for i in range(self.COLOR_VARIATION_SIZE):
            self.surf[i] = self.init_surface(i)

    def update(self, on_shield):
        if on_shield:
            if 0 < self.sp:
                self.sp += self.SP_CONSUME_UNIT
        else:
            if self.sp < self.SP_MAX_VALUE:
                self.sp += self.SP_RECOVER_UNIT

    def draw(self, airframe, screen):
        if not (0 < self.sp):
            return
        x = airframe.x - airframe.AIRFRAME_BOT_WIDTH / 2 - self.RADIUS / 2
        y = airframe.y - self.RADIUS / 2
        i = int(self.COLOR_VARIATION_SIZE * self.sp / self.SP_MAX_VALUE) - 1
        if i < 0:
            i = 0
        screen.blit(self.surf[i], (x, y), special_flags=pyglocal.BLEND_SUB)
