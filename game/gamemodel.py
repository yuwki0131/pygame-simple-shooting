# local files
import const
import objects
import ufo
import burn as burner
from player import Player
# utilities
from calcutil import add
from calcutil import touched_with_player
from calcutil import touched_with_shield

# ----------------------------------------------------------------
# game model
# ----------------------------------------------------------------


class Game:
    """ control game flow  & manage game score"""

    LEVEL_NAME = ["Easy", "Normal", "Hard", "Extra Hard"]
    LEVEL_MAX = len(LEVEL_NAME)

    def __init__(self):
        self.reset()
        self.start = False
        self.level = 1

    def reset(self):
        "called when init or reboot"
        self.over = False
        self.pause = False
        self.score = 0
        self.lastscore = 0
        self.cowscore = 0
        self.alienscore = 0

    def add_score(self, value):
        self.score += value

    def inc_cow(self):
        self.cowscore += 1

    def dec_cow(self):
        self.cowscore -= 1

    def inc_alien(self):
        self.alienscore += 1

    def dec_alien(self):
        self.alienscore -= 1

    def backup_score(self):
        self.lastscore = self.score

    def up_level(self):
        self.level = (self.level + 1) % Game.LEVEL_MAX

    def down_level(self):
        self.level = (self.level - 1) % Game.LEVEL_MAX

    def get_level_text(self):
        return Game.LEVEL_NAME[self.level]


class Control:
    """ entity of player's inputs """

    def __init__(self):
        self.reset()

    def reset(self):
        "called when init or reboot"
        self.on_shield = False
        self.on_fire = False
        self.fire_alien = False
        self.fire_missile = False
        self.press_add = (0, 0)

    def move_up(self):
        self.press_add = add(self.press_add, (0, -Player.AIRFRAME_MOVEUNIT))

    def move_down(self):
        self.press_add = add(self.press_add, (0, Player.AIRFRAME_MOVEUNIT))

    def move_left(self):
        self.press_add = add(self.press_add, (-Player.AIRFRAME_MOVEUNIT, 0))

    def move_right(self):
        self.press_add = add(self.press_add, (Player.AIRFRAME_MOVEUNIT, 0))


def generate(constructor, n):
    "generate Array of n objects"
    return [constructor() for _ in range(n)]


class FieldObjects:
    """ manage field objects """

    def __init__(self, game):
        self.game = game
        self.init_field_objects()

    def init_field_objects(self):
        "initialize arrays of field objects"
        # buring points
        self.burnpoints = burner.BurnPoints()

        # bullets of player
        self.bullet1_array = generate(objects.BulletType1, 100)
        self.missile_array = generate(objects.Missile, 30)
        self.bullet_alien_array = generate(objects.BulletAlien, 10)
        self.player_bullets = (self.bullet1_array + self.missile_array +
                               self.bullet_alien_array)
        # ufo
        self.enemies = generate((lambda: ufo.UFO(self, self.game)), 20)

        # items
        self.item_bolt_array = generate(objects.ItemBolt, 6)
        self.item_star_array = generate(objects.ItemStar, 6)
        self.item_alien_array = generate(objects.ItemAlien, 3)
        self.item_cow_array = generate(objects.ItemCow, 3)
        self.all_items_array = (self.item_bolt_array + self.item_star_array +
                                self.item_alien_array + self.item_cow_array)
        # bullets of enemy
        self.bullet2_array = generate(objects.BulletType2, 60)
        self.bullet3_array = generate(objects.BulletType3, 60)
        self.enemy_bullets = self.bullet2_array + self.bullet3_array

        # all bullets
        self.all_bullets_array = self.player_bullets + self.enemy_bullets
        self.all_items_bullets = self.all_items_array + self.all_bullets_array
        self.withoutplayer = self.enemies + self.all_items_bullets

    def __move_enemies(self):
        "move enemies (call update functinos)"
        for enemy in self.enemies:
            if enemy.state:
                enemy.update()

    def __move_objs(self):
        "move objects (call update functinos)"
        for obj in self.all_items_bullets:
            if obj.state:
                obj.update()
                if obj.outof_window():
                    obj.off()

    def update(self):
        "update for each field objects"
        self.__move_enemies()
        self.__move_objs()
        self.__detect_collision(self.game, self.player)
        self.burnpoints.update()

    def touched_any_enemies(self, enemy_posistion, damage):
        "collision detection between enemy(x,y) and player's bullets"
        x, y = enemy_posistion
        for enemy in self.enemies:
            if enemy.state and enemy.touch_at(x, y):
                self.burnpoints.add((enemy_posistion, const.BURNWAIT_STANDARD))
                if enemy.isfreeze:
                    return True
                enemy.get_damage(damage)
                enemy.get_action(damage)
                self.game.add_score(damage)
                return True
        return False

    def __detect_collision(self, game, player):
        "detect collision and invoke actions"
        # defence (from enemy to player)
        if self.game.over:
            return
        # enemy bullets
        for bullet in self.enemy_bullets:
            if not bullet.state:
                continue
            xy, wait = bullet.getxy(), bullet.burnwait
            if player.shield_enabled():
                if touched_with_shield(player, xy):
                    bullet.off()
                    self.burnpoints.add((xy, wait))
                continue
            if touched_with_player(player, xy):
                bullet.off()
                player.get_damage(bullet.damage)
                self.burnpoints.add((xy, wait))
        # player bullets
        for bullet in self.player_bullets:
            if bullet.state:
                if self.touched_any_enemies(bullet.getxy(), bullet.damage):
                    bullet.off()
        # items
        for obj in self.all_items_array:
            if obj.state:
                if touched_with_player(player, obj.getxy()):
                    obj.off()
                    obj.event(player, game)
