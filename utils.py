import pygame
import math
import os
from hashlib import md5


# load a single image
def load_tpng(assets_path):
    img = pygame.image.load("assets/" + assets_path).convert_alpha()
    return img


# load all images in a directory
def load_tpng_folder(assets_path):

    images = []

    # remove trailing slash in case it was added
    if assets_path[-1] == "/":
        assets_path = assets_path[:-1]

    full_path = "assets/" + assets_path

    for img_name in sorted(
        os.listdir(full_path)
    ):  # sorted is used for OS interoperability
        images.append(load_tpng(assets_path + "/" + img_name))

    return images


class Vector2:
    def __init__(self, x, y = None):

        # if we didn't get a y check if we got a tuple
        # and if we did, unpack it. Otherwise, set y to x

        if y is None:
            if type(x) is tuple:
                self.x = x[0]
                self.y = x[1]
            else:
                self.x = x
                self.y = x

        # in this case we got both x and y so we can just set them
        else:
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
            if colorkey == -1:
                colorkey = self.sheet.get_at((0, 0))

            # check if color is a tuple now
            if type(colorkey) is tuple:
                self.sheet.set_colorkey(colorkey)

    def get_at(self, x, y, width, height):
        return self.sheet.subsurface(x, y, width, height)

    def dice(self, width, height):
        images = []
        for y in range(0, self.sheet.get_height(), height):
            for x in range(0, self.sheet.get_width(), width):
                images.append(self.sheet.subsurface(x, y, width, height))
        return images

    def dice_to_folder(self, width, height, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            print("Folder already exists")
            return
        count = 0
        for y in range(0, self.sheet.get_height(), height):
            for x in range(0, self.sheet.get_width(), width):
                count += 1
                pygame.image.save(self.sheet.subsurface(x, y, width, height), folder + "/%d-%d_%d.png" % (count-1, x, y))

# animation class (DaFluffyPotato)
class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def reset(self):
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

class Seed:
    """
    This class represents a Seed object.

    Attributes:
        __seed (str): The seed value. Default is "Peach".

    Methods:
        get_seed(): Returns the current seed value.
        set_seed(seed: str): Sets a new seed value.
    """

    def __init__(self, seed: str = "Peach"):
        """
        The constructor for Seed class.

        Parameters:
            seed (str): The seed value. Default is "Peach".
        """
        self.__seed = seed

    def get_seed(self):
        """
        The function to get the current seed value.

        Returns:
            str: The current seed value.
        """
        return self.__seed

    def set_seed(self, seed: str = "Peach"):
        """
        The function to set a new seed value.

        Parameters:
            seed (str): The new seed value. Default is "Peach".
        """
        self.__seed = seed

    def __hashed(self, name: str = "default"):
        """
        The function to return a hashed value based on the seed and the name.
        """

        # generate md5 hash from the seed and the name
        result = md5((self.__seed + name).encode()).hexdigest()
        # print("Seed: ", self.__seed, "Name: ", name, "Hash: ", result)
        return result

    def float(self, name: str = "default") -> float:
        """
        The function to return a 0-1 float value based on the seed and the name.
        """

        result = self.__hashed(name)

        # convert the hash to a float value between 0 and 1
        return int(result, 16) / 16**32


    def bool(self, name: str = "default") -> bool:
        """
        The function to return a boolean value based on the seed and the name.
        """

        result = self.__hashed(name)
        return int(result, 16) % 2 == 0

    def int(self, name: str = "default", min: int = 0, max: int = 1_000_000) -> int:
        """
        The function to return an integer value based on the seed and the name.
        The minimum value is inclusive and the maximum value is exclusive.
        By default, the minimum value is 0 and the maximum value is 1,000,000.
        """

        result = self.__hashed(name)
        return int(result, 16) % (max - min) + min


if __name__ == "__main__":
    # test the Seed class
    seed = Seed("Peach")
    for i in range(8):
        print(seed.int("testing the seed trial #" + str(i)))
        print(seed.bool("testing the seed trial #" + str(i)))
        print(seed.float("testing the seed trial #" + str(i)))

    # test the Vector2 class
    a = Vector2(1, 2)
    print(a.pos())

    b = Vector2((1, 2))
    print(b.pos())

    c = a + b
    print(c.pos())

    d = Vector2(1)
    print(d.pos())
