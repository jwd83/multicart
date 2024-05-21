# a scene that simulates TV static
import random
import pygame
from scene import Scene
import settings


class TVStatic(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.time_static = 0.25
        self.time_blank = 0.1
        self.time_total = self.time_static + self.time_blank

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if self.elapsed() > self.time_total:
            self.game.scene_replace = "JackGames"

    def draw(self):
        self.screen.fill((0, 0, 0))

        box_size = 5

        # only draw static if we're in the static phase
        if self.elapsed() < self.time_static:
            for x in range(0, settings.RESOLUTION[0], box_size):
                for y in range(0, settings.RESOLUTION[1], box_size):
                    if random.randint(0, 1) == 0:
                        pygame.draw.rect(
                            self.screen, (255, 255, 255), (x, y, box_size, box_size)
                        )
