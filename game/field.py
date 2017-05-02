class Field:
    """ define field size and limits """
    x = 480
    y = 640

    # movable range
    LEFTMOST = 20
    RIGHTMOST = x - 30
    TOPMOST = 50
    BOTMOST = y - 80
    ENEMY_TOPMOST = 80
    ENEMY_BOTMOST = y - 180

    # closer alert range
    CLOSER_RANGE = 30
    LEFT_CLOSER = LEFTMOST + CLOSER_RANGE
    RIGHT_CLOSER = RIGHTMOST - CLOSER_RANGE
    TOP_CLOSER = TOPMOST + CLOSER_RANGE
    BOT_CLOSER = BOTMOST - CLOSER_RANGE

    # field far most
    FARTHEST = (x + y) * 2

    # field (x, y)
    XY = (x, y)

    # player's init center
    PLAYER_INIT_CENTER_X, PLAYER_INIT_CENTER_Y = (x / 2, y * (3 / 4))

    def x_in_movablerange(x):
        "check x of player posision"
        return Field.LEFTMOST < x < Field.RIGHTMOST

    def y_in_movablerange(y):
        "check y of player posision"
        return Field.TOPMOST < y < Field.BOTMOST

    def is_enemy_y_in_movable_range(y):
        "check y of emeny position"
        return Field.TOPMOST < y < Field.ENEMY_BOT_MOST

    def close_to_wall(x, y):
        "check object closer to wall"
        return (x < Field.LEFT_CLOSER or Field.RIGHT_CLOSER < x or
                y < Field.TOP_CLOSER or Field.BOT_CLOSER < y)

    def outof_field(x, y):
        "check object out of field"
        return not(0 <= x <= Field.x and 0 <= y <= Field.y)

    def modify_x(x):
        "fix x posision, if out of range"
        if x < Field.LEFTMOST:
            return Field.LEFTMOST
        if Field.RIGHTMOST < x:
            return Field.RIGHTMOST
        return x

    def modify_y(y):
        "fix y posision, if out of range"
        if y < Field.TOPMOST:
            return Field.TOPMOST
        if Field.BOTMOST < y:
            return Field.BOTMOST
        return y

    def modify_y_of_enemy(y):
        "fix y posision, if out of range for enemy"
        if y < Field.ENEMY_TOPMOST:
            return Field.ENEMY_TOPMOST
        if Field.ENEMY_BOTMOST < y:
            return Field.ENEMY_BOTMOST
        return y
