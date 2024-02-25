import scene
import pygame
import random
import settings


class Star:
    def __init__(self):
        self.max_size = 4
        self.min_brightness = 100

        # set the size
        self.size = 0
        self.resize()

        # set the start position
        self.x = random.randint(0, settings.RESOLUTION[0])
        self.y = random.randint(0, settings.RESOLUTION[1])

    def resize(self):
        self.size = 1 + random.random() * (self.max_size - 1)
        self.recolor()

    def recolor(self):
        self.intensity = self.min_brightness + (
            (self.size / self.max_size) * (255 - self.min_brightness)
        )
        self.color = (self.intensity, self.intensity, self.intensity)

    def move(self):
        self.x -= self.size / 2
        # self.twinkle()

        if self.x < -self.size:
            self.resize()
            self.x = settings.RESOLUTION[0] + self.size
            self.y = random.randint(0, settings.RESOLUTION[1])

    def twinkle(self):
        # 10 % chance to twinkle
        if random.randint(0, 100) < 10:
            # 50% chance to flicker blue or red
            if random.randint(0, 1):
                if random.randint(0, 1):
                    self.color = (0, 0, 255)
                else:
                    self.color = (255, 0, 0)
            else:
                self.color = (255, 255, 255)
            # self.color = (self.intensity, self.intensity, self.intensity)
        else:
            self.recolor()


class Starfield(scene.Scene):
    def __init__(self, game):
        super().__init__(game)

        # load the title screen
        self.game.scene_push = "Title"

        # create a list of 100 stars
        self.stars = [Star() for _ in range(100)]

    def update(self):
        pass

    def draw(self):
        # set the screen to black
        self.screen.fill((0, 0, 0))

        # move then draw each star
        for star in self.stars:
            star.move()

            pygame.draw.circle(self.screen, star.color, (star.x, star.y), star.size)
