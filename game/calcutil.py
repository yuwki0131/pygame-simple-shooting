import random


def once_in(n):
    "returns true when once in n times"
    return random.randint(0, n) == 1


def in_circle(x, y, r):
    "(x, y) in the ciecle(radius=r, center=origin)"
    return x ** 2 + y ** 2 <= r ** 2


def diff(a, b):
    "diff a&b vectors"
    x0, y0 = a
    x1, y1 = b
    return (x1 - x0, y1 - y0)


def add(a, b):
    "add a&b vectors"
    x0, y0 = a
    x1, y1 = b
    return (x1 + x0, y1 + y0)


def prod(a, b):
    "prod a&b vectors"
    x0, y0 = a
    x1, y1 = b
    return x0 * y1 - x1 * y0


def touched_with_player(player, xy):
    "detect collision between player and object(xy)"
    p = player.getxy()
    xchead = diff(player.AIRFRAME_HEAD, (0, 0))
    xcleft = diff(player.AIRFRAME_LEFT, (0, 0))
    xcright = diff(player.AIRFRAME_RIGHT, (0, 0))
    a, b, d = add(xchead, xy), add(xcleft, xy), add(xcright, xy)
    va = prod(diff(d, a), diff(a, p))
    vb = prod(diff(b, d), diff(d, p))
    vd = prod(diff(a, b), diff(b, p))
    return (va < 0 and vb < 0 and vd < 0) or (va > 0 and vb > 0 and vd > 0)


def touched_with_shield(player, xy):
    "detect collision between shield(c) and object(xy)"
    x, y = xy
    xc = player.x + player.AIRFRAME_BOT_WIDTH / 2 - 10
    yc = player.y + player.AIRFRAME_HEIGHT / 2 - 10
    return in_circle((x - xc), (y - yc), player.shield.RADIUS)
