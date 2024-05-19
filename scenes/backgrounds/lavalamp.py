import pygame
from scene import Scene
from utils import *
import random
import settings


class Blob:
    def __init__(self):

        # random starting position
        self.x = random.randint(0, settings.RESOLUTION[0])
        self.y = random.randint(0, settings.RESOLUTION[1])

        # random velocity
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)

        # random color
        self.color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

        # random size
        self.size = random.randint(10, 30)

        # mutation values
        self.ds = random.uniform(-0.5, 0.5)  # random change in size
        self.dr = random.randint(-5, 5)  # random change in red color
        self.dg = random.randint(-5, 5)  # random change in green color
        self.db = random.randint(-5, 5)  # random change in blue color

        self.color_step = 0
        self.color_step_rate = random.randint(3, 7)

    def constrain(self, n, n_min, n_max):
        return max(min(n_max, n), n_min)

    def mutate(self):

        # update size
        self.size += self.ds
        # if size goes out of bounds, reverse its direction
        if not (10 <= self.size <= 50):
            self.ds *= -1

        # update color if it's time
        self.color_step += 1

        if self.color_step % self.color_step_rate == 0:
            # print("stepping color")
            r, g, b = self.color
            r = self.constrain(r + self.dr, 0, 255)
            g = self.constrain(g + self.dg, 0, 255)
            b = self.constrain(b + self.db, 0, 255)
            self.color = (r, g, b)
            # if color hits a bound, reverse its direction
            if (r == 0) or (r == 255):
                self.dr *= -1
            if (g == 0) or (g == 255):
                self.dg *= -1
            if (b == 0) or (b == 255):
                self.db *= -1


class LavaLamp(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.blobs = [Blob() for _ in range(50)]

    def update(self):
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        for blob in self.blobs:
            blob.mutate()
            blob.x += blob.dx
            blob.y += blob.dy
            # if blob hits the edge of the screen, reverse its velocity
            if not (0 <= blob.x <= settings.RESOLUTION[0]):
                blob.dx *= -1
            if not (0 <= blob.y <= settings.RESOLUTION[1]):
                blob.dy *= -1

        for blob in self.blobs:
            pygame.draw.circle(
                self.screen, blob.color, (blob.x, blob.y), blob.size
            )  # draw blob as a circle
