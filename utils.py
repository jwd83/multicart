import pygame
import os
from hashlib import md5
import random
import math
import settings


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


# Draws a grid covering the specified screen, with the optional tile_size and color arguments.
# Default color is an off-white.
def draw_grid(surf, tile_size=16, color=(242, 245, 255)):
    width = surf.get_width()
    height = surf.get_height()

    for x in range(0, int(width // tile_size) + 1):
        pygame.draw.line(surf, color, (0, x * tile_size), (width, x * tile_size))
        pygame.draw.line(surf, color, (x * tile_size, 0), (x * tile_size, height))


class Button:  # todo remove this in favor of classes.button
    def __init__(
        self,
        screen,
        pos: tuple[int, int],
        size: tuple[int, int],
        content: str | pygame.surface.Surface,
        # properties for text buttons
        font=None,
        fontSize=32,
        color=(255, 255, 255),
    ):

        self.screen = screen

        # If our content is a string, render the text onto a surface with any given settings
        if type(content) == str:
            self.image = pygame.transform.scale(
                self.make_text(content, color, fontSize, font), size
            )
        # otherwise it should be a surface, so we can just assign it to our image
        else:
            self.image = content

        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.clicked = False
        self.last_pressed = False
        self.activating = False

    def make_text(
        self,
        text,
        color,
        fontSize,
        font=None,
        stroke=False,
        strokeColor=(0, 0, 0),
        strokeThickness=1,
    ):
        if font is None:
            font = "assets/fonts/" + settings.FONT

        if font == "system-ui":
            font = None

        # if we aren't stroking return the text directly
        if not stroke:
            return pygame.font.Font(font, fontSize).render(text, 1, color)

        # if we are stroking, render the text with the stroke
        # first render the text without the stroke

        # create a version of the text in the stroke color and blit it to the surface
        surf_text = pygame.font.Font(font, fontSize).render(text, 1, color)
        surf_text_stroke = pygame.font.Font(font, fontSize).render(text, 1, strokeColor)

        # create a transparent surface to draw the text and stroke on
        size = (
            surf_text.get_width() + strokeThickness * 3,
            surf_text.get_height() + strokeThickness * 3,
        )
        surface = self.make_transparent_surface(size)

        # blit the stroke text to the surface
        for i in range(strokeThickness * 2 + 1):
            for j in range(strokeThickness * 2 + 1):
                surface.blit(surf_text_stroke, (i, j))

        # blit the text on top of the stroke
        surface.blit(surf_text, (strokeThickness, strokeThickness))

        # return the surface
        return surface

    def draw(self):
        action = False

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        in_button = self.rect.collidepoint(mouse_pos)

        # detect our mouse button down and up frame
        mouse_down = False
        mouse_up = False
        if mouse_pressed != self.last_pressed:
            mouse_down = mouse_pressed
            mouse_up = not mouse_pressed
        self.last_pressed = mouse_pressed

        if not in_button:
            # if the mouse leaves the button deactivate it
            self.activating = False
        else:

            # begin activating on a mouse button down inside the button
            if mouse_down:
                self.activating = True

            # confirm activation on a mouse button up inside the button
            if mouse_up and self.activating:
                action = True
                self.activating = False

        # offset button for float/pending activation
        offset = self.rect.copy()
        if self.activating:
            # draw our button indented while activating
            offset.x += 2
            offset.y += 2
        else:
            # draw the mouse hover outdent while hovered
            if in_button:
                offset.x -= 1
                offset.y -= 1

        self.screen.blit(self.image, offset)
        return action


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
