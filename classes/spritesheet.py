import pygame
import os


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
