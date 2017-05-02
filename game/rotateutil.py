import pygame
import pygame.gfxdraw
# utilities
from calcutil import add


def rotate(screen, picture, rect, angle, x, y):
    "rotate picture with angle"
    rotated = pygame.transform.rotate(picture, angle)
    size = rotated.get_size()
    pos = (rect.x + rect.w / 2 - size[0] / 2,
           rect.y + rect.h / 2 - size[1] / 2)
    screen.blit(rotated, add(pos, (x, y)))
