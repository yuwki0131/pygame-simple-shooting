import math
import pygame
import pygame.gfxdraw
import pygame.locals as pyglocal
# local files
import const
import burn as burner
from const import Colors
from field import Field
# utilities
from calcutil import in_circle
from rotateutil import rotate
from imgutil import ImageLoader


class FieldObjRoot:

    def reset(self, x, y):
        self.x0, self.y0 = x, y
        self.state = True

    def getxy(self):
        return self.x0, self.y0

    def off(self):
        self.state = False

    def outof_window(self):
        x, y = self.getxy()
        return Field.outof_field(x, y)


class Missile(FieldObjRoot):
    damage = 30
    burnwait = const.BURNWAIT_STANDARD * 1.5
    surf = None

    def __init__(self):
        self.state = False
        self.theta = 0
        if not Missile.surf:
            Missile.surf = ImageLoader.load_with_trans("missile.png", (20, 20))

    def reset(self, x, y):
        self.x0, self.y0 = x, y
        self.state = True
        self.target = None

    def lockon(self, enemy):
        self.target = enemy

    def update(self):
        self.y0 -= 1
        if not self.target:
            return
        x, y = self.target.getxy()
        self.x0 += (x - self.x0) / 50
        self.theta = 0.5 / (x - self.x0) / Field.y * 10

    __rotate_rect = pyglocal.Rect(0, 0, 18, 22)

    def draw(self, screen, _):
        x, y = int(self.x0) + 4, int(self.y0)
        burner.draw_gunburn(screen, x + 9, y + 24)
        rotate(screen, self.surf, Missile.__rotate_rect, 0, x, y)


class BulletAlien(FieldObjRoot):
    damage = 0
    burnwait = 0
    surf = None

    def __init__(self):
        self.state = False
        if not BulletAlien.surf:
            BulletAlien.surf = ImageLoader.load_with_trans(
                "alien.png", (30, 30))

    def update(self):
        self.y0 -= 0.5

    def draw(self, screen, _):
        x, y = int(self.x0) - 15, int(self.y0) - 15
        screen.blit(self.surf, (x, y))
        burner.draw_gunburn(screen, x + 15, y + 31)


class BulletType1(FieldObjRoot):
    damage = 2
    burnwait = const.BURNWAIT_STANDARD * 0.5

    BEAM_LENGTH = 10

    def __init__(self):
        self.state = False

    def update(self):
        self.y0 -= 3

    def draw(self, screen, _):
        x, y = int(self.x0) + 4, int(self.y0)
        pygame.gfxdraw.line(screen, x, y, x, y + self.BEAM_LENGTH,
                            (255, 225, 0))
        pygame.gfxdraw.line(screen, x + 1, y + 1, x + 1, y + self.BEAM_LENGTH,
                            (255, 0, 0))


class BulletType2(FieldObjRoot):
    damage = -2
    burnwait = const.BURNWAIT_STANDARD * 0.5

    BEAM_LENGTH = 15

    def __init__(self):
        self.state = False

    def update(self):
        self.y0 += 2

    def draw(self, screen, _):
        x, y = int(self.x0), int(self.y0)
        pygame.gfxdraw.line(screen, x, y, x, y + self.BEAM_LENGTH,
                            (0, 225, 225))
        pygame.gfxdraw.line(screen, x + 1, y, x + 1, y + self.BEAM_LENGTH,
                            (0, 225, 225))


class BulletType3(FieldObjRoot):

    def init_surface(self):
        r = 4
        surf = pygame.Surface((r * 2 + 1, r * 2 + 1))
        surf.fill(Colors.BLACK)
        for i in range(4):
            color = (50 + i * 40, 0, 50 + i * 40)
            pygame.draw.circle(surf, color, (r, r), int(r - i))
        surf.set_colorkey(Colors.WHITE, pyglocal.RLEACCEL)
        return surf

    damage = -4
    burnwait = const.BURNWAIT_STANDARD * 0.4
    surf = None

    def __init__(self):
        self.state = False
        if not BulletType3.surf:
            BulletType3.surf = self.init_surface()

    def reset(self, x, y, theta):
        self.x0, self.y0 = x, y
        self.theta = theta
        self.state = True
        self.r = 0
        self.n = 1

    def update(self):
        self.n += 1
        self.r += 0.5 + 5 / self.n

    def getxy(self):
        x = math.cos(math.pi * 2 * self.theta) * self.r + self.x0
        y = math.sin(math.pi * 2 * self.theta) * self.r + self.y0
        return x, y

    def draw(self, screen, _):
        x, y = self.getxy()
        xy = (int(x) - 8, int(y) - 8)
        screen.blit(self.surf, xy, special_flags=pyglocal.BLEND_SUB)

    def touch_at(self, x, y):
        cx, cy = self.getxy()
        return in_circle(cx - x, cy - y, 3)


class ItemObjectRoot(FieldObjRoot):

    def getxy(self):
        x = math.cos(math.pi * 2 * self.theta) * self.r + self.x0
        y = math.sin(math.pi * 2 * self.theta) * self.r + self.y0
        return x, y

    def reset(self, x, y, theta):
        self.x0, self.y0 = x, y
        self.r = 0
        self.theta = theta
        self.state = True

    def update(self):
        self.r += 0.4

    __rotate_rect = pyglocal.Rect(0, 0, 40, 30)

    def draw(self, screen, game):
        x, y = self.getxy()
        if not game.pause:
            self.rotatecounter += 0.9
        rotate(screen, self.surf, self.__rotate_rect, self.rotatecounter,
               x - 20, y - 15)


class ItemAlien(ItemObjectRoot):
    surf = None

    def __init__(self):
        self.state = False
        self.rotatecounter = 0
        if not ItemAlien.surf:
            ItemAlien.surf = ImageLoader.load_with_trans("alien.png", (30, 30))

    def event(self, player, game):
        game.inc_alien()


class ItemCow(ItemObjectRoot):
    surf = None

    def __init__(self):
        self.state = False
        self.rotatecounter = 0
        if not ItemCow.surf:
            ItemCow.surf = ImageLoader.load_with_trans("cow.png", (30, 30))

    def update(self):
        self.y0 += 1

    def draw(self, screen, _):
        x, y = self.getxy()
        self.rotatecounter += 0.9
        rotate(screen, self.surf, pyglocal.Rect(0, 0, 40, 30),
               self.rotatecounter, x - 20, y - 15)

    def event(self, player, game):
        game.inc_cow()


class ItemStar(ItemObjectRoot):
    surf = None

    def __init__(self):
        self.state = False
        self.rotatecounter = 0
        if not ItemStar.surf:
            ItemStar.surf = ImageLoader.load_with_trans("star.png", (20, 20))

    def event(self, player, game):
        player.get_dual()


class ItemBolt(ItemObjectRoot):
    surf = None

    def __init__(self):
        self.state = False
        self.rotatecounter = 0
        if not ItemBolt.surf:
            ItemBolt.surf = ImageLoader.load_with_trans("bolt.png", (20, 20))

    def event(self, player, game):
        player.recover_hp10()
