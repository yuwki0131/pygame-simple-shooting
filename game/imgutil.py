import os
import pygame

# scaling and load image


class ImageLoader:

    @staticmethod
    def load_with_trans(img_name, xy_size):
        "load image to surface with transparent"
        file_name = os.path.dirname(__file__) + "/img/" + img_name
        image = pygame.image.load(file_name).convert_alpha()
        obj = pygame.transform.smoothscale(image, xy_size)
        trans_color = obj.get_at((0, 0))
        obj.set_colorkey(trans_color, pygame.locals.RLEACCEL)
        return obj
