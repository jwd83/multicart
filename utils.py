import pygame
import os
from hashlib import md5
import random
import math


# a function to map ranges between two values
def interpolate(in_value, in_min, in_max, out_min, out_max):
    # check for division by zero
    if in_max - in_min == 0:
        raise ValueError("Division by zero")
    return (in_value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


# load a single image
def load_tpng(assets_path) -> pygame.Surface:
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


class SpriteSheet:
    def __init__(self, asset_path: str, colorkey: tuple = None):
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
                pygame.image.save(
                    self.sheet.subsurface(x, y, width, height),
                    folder + "/%d-%d_%d.png" % (count - 1, x, y),
                )


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
        __seed (str): The seed value. Default is None which
        generates a random seed.

    Methods:
        get_seed(): Returns the current seed value.
        set_seed(seed: str): Sets a new seed value.
    """

    def __init__(self, seed: str | None = None):
        """
        The constructor for Seed class.

        Parameters:
            seed (str): The seed value. Default is "Peach".
        """
        if seed is None:
            # generate a random string to be used as a seed
            self.__seed = str(random.random())
        else:
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

    def choice(self, name: str = "default", choices: list = []) -> any:
        """
        The function to return a random choice from a list based on the seed and the name.
        """

        if len(choices) == 0:
            return None

        result = self.__hashed(name)
        return choices[int(result, 16) % len(choices)]


def blit_outline(source: pygame.Surface, target: pygame.Surface, dest: tuple):

    mask = pygame.mask.from_surface(source)
    mask.invert()
    mask = mask.to_surface()
    mask.set_colorkey((255, 255, 255))

    x = dest[0]
    y = dest[1]

    target.blit(mask, (x - 1, y))
    target.blit(mask, (x + 1, y))
    target.blit(mask, (x, y - 1))
    target.blit(mask, (x, y + 1))


# test our utilities if ran directly
if __name__ == "__main__":
    # test the Seed class
    seed = Seed("Peach")
    for i in range(8):
        print(seed.int("testing the seed trial #" + str(i)))
        print(seed.bool("testing the seed trial #" + str(i)))
        print(seed.float("testing the seed trial #" + str(i)))

    for i in range(10):
        r = Seed()
        sum = 0
        for j in range(100000):
            sum += r.float(f"test {j}:{i}")
        print(sum)
