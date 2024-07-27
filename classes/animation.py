import pygame
import os


class Animation(pygame.sprite.Sprite):
    def __init__(self, images: list[pygame.Surface] | str, img_dur=5, loop=True):
        """Create an Animation object from a list of images or a string
        representing a path to a folder containing images.

        Args:
            images (list[pygame.Surface] | str): A list of surface or a string path to a folder containing images. Required.
            img_dur (int, optional): The ratio of amount of frames displayed to screen for each frame of animation. Defaults to 5.
            loop (bool, optional): Should the animation loop or end on it's last frame. Defaults to True.
        """
        pygame.sprite.Sprite.__init__(self)

        if isinstance(images, list):
            self.images = images
        elif isinstance(images, str):
            self.images = self.load_images(images)

        self.image = self.images[0]
        self.rect = self.image.get_rect()
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

        self.image = self.images[int(self.frame / self.img_duration)]

    def img(self):
        return self.images[int(self.frame / self.img_duration)]

    def reset(self):
        self.frame = 0
        self.done = False
        self.image = self.images[0]

    # load a single image
    def __load_image(self, path) -> pygame.Surface:
        img = pygame.image.load(path).convert_alpha()
        return img

    # load all images in a directory
    def load_images(self, path) -> list[pygame.Surface]:
        images = []

        for img_name in sorted(os.listdir(path)):
            # sorted is used for OS interoperability
            images.append(self.__load_image(path + "/" + img_name))

        return images

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
