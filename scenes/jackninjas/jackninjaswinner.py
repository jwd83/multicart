import pygame
from scene import Scene
from utils import *


class JackNinjasWinner(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.Text(
            text="You Won!",
            pos=(self.game.screen.get_width() / 2, self.game.screen.get_height() / 2),
            anchor="center",
        )

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.TextDraw()
