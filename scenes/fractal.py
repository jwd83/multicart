import pygame
from scene import Scene
from utils import *
import settings


class Fractal(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.texts = {
            "title": self.Text(
                "Fractal",
                settings.RESOLUTION[0] // 2,
                settings.RESOLUTION[1] // 2,
                50,
                "center",
            ),
        }

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))
