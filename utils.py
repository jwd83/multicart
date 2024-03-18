import pygame
import math

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2)

    # compute the new normalized vector that will have a fixed length of 1
    def normalize_velocity(self):
        # store the result of the current magnitude at the time of calling
        result = self.magnitude()
        if result != 0:
            self.x /= result
            self.y /= result

    # scale the velocity of the current vector taking the magnitude of the vector into account
    # and using the max_x_or_y_from_origin to scale the velocity of the vector
    def scale_velocity(self):
        max_x_or_y_from_origin = max(abs(self.x), abs(self.y))

        if max_x_or_y_from_origin != 0:

            result = self.magnitude()
            self.x = (self.x / result) * max_x_or_y_from_origin
            self.y = (self.y / result) * max_x_or_y_from_origin

    def pos(self):
        return (self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

class SpriteSheet:
    def __init__ (self, asset_path: str, colorkey: tuple = None):
        self.asset_path = "assets/" + asset_path
        self.sheet = pygame.image.load(self.asset_path).convert_alpha()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = self.sheet.get_at((0, 0))

            # check if color is a tuple now
            if type(colorkey) is tuple:
                self.sheet.set_colorkey(colorkey)


# animation class (DaFluffyPotato)
class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]