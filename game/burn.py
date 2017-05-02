import math
import random
import pygame
import pygame.gfxdraw
import pygame.locals as pyglocal
# local files
from const import Colors


class BurnPoints:
    """ Burning Points Manager """

    class Burn:
        """ Burning Point"""

        def __init__(self):
            self.x = 0
            self.y = 0
            self.wait = 0
            self.state = False

        def reset(self, x, y, wait):
            self.x = x
            self.y = y
            self.wait = wait
            self.state = True

        def get_params(self):
            return (self.x, self.y, self.wait)

        def off(self):
            self.state = False

        def decrement_and_off(self):
            self.wait -= 1
            if self.wait <= 0:
                self.state = False

    def __init__(self):
        self.points = [BurnPoints.Burn() for _ in range(100)]

    def reset(self):
        for point in self.points:
            point.off()

    def add(self, xyt):
        xy, t = xyt
        x, y = xy
        for point in self.points:
            if not point.state:
                point.reset(x, y, t)
                return

    def update(self):
        for point in self.points:
            if point.state:
                point.decrement_and_off()


# number of zigzag of burning draw
BURNING_ZIGZAG = 10
# small burning size array (for each layer)
SMALL_BURNING_SIZE_ARRAY = [8, 6, 4]
# normal burning size array (for each layer)
NORMAL_BURNING_SIZE_ARRAY = [12, 10, 8]
# large burning size array (for each layer)
LARGE_BURNING_SIZE_ARRAY = [14, 12, 10]
# burning layer limit (~= buring time limit)
BURNING_LAYER_MAX = 500


def anglexr(rate, r, x):
    return math.cos(math.pi * 2 * rate) * random.random() * r + x


def angleyr(rate, r, y):
    return math.sin(math.pi * 2 * rate) * random.random() * r + y


def create_burninglayer(r, x, y):
    "create burning points"
    return [(anglexr(n / BURNING_ZIGZAG, r, x),
             angleyr(n / BURNING_ZIGZAG, r, y))
            for n in range(BURNING_ZIGZAG)]


def draw_burning_with_size(screen, x, y, size_array):
    "draw burning with size array"
    for i, size in enumerate(size_array):
        color = Colors.BURN_GRADATION[i]
        layer = create_burninglayer(size, x, y)
        pygame.draw.polygon(screen, color, layer)


def draw_gunburn(screen, x, y):
    "draw gun burn : burn for player's gunburn, missile and alien missile"
    draw_burning_with_size(screen, x, y, SMALL_BURNING_SIZE_ARRAY)


class BuriningDrawer:
    """ Burning Drawer """

    def __init__(self):
        self.burnlayers = list()
        burn_lt = 50
        for i in range(BURNING_LAYER_MAX):
            surf = pygame.Surface((burn_lt * 2, burn_lt * 2))
            draw_burning_with_size(surf, burn_lt, burn_lt,
                                   NORMAL_BURNING_SIZE_ARRAY)
            for i in range(5):
                x = burn_lt + random.randint(0, 4)
                y = burn_lt + random.randint(0, 4)
                draw_burning_with_size(surf, x, y, LARGE_BURNING_SIZE_ARRAY)
            surf.set_colorkey(Colors.BLACK, pyglocal.RLEACCEL)
            surf.convert_alpha()
            self.burnlayers.append(surf)

    def draw_burning(self, screen, burnpoints):
        "draw general burning"
        burn_lt = 50
        for point in burnpoints.points:
            if point.state:
                x, y, t = point.get_params()
                xy = (x - burn_lt, y - burn_lt)
                screen.blit(self.burnlayers[int(t)], xy)
