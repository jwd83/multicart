import pygame
from scene import Scene
from utils import *


class JackNinjasInventory(Scene):
    def __init__(self, game):
        super().__init__(game)
        pos = (self.game.WIDTH // 2, 20)
        self.Text(text="Inventory", pos=pos, anchor="center")

    def update(self):
        # if the user presses escape show the menu
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_i in self.game.just_pressed:
            self.game.scene_pop = True

    def draw(self):
        # self.screen.fill((0, 0, 0))
        self.TextDraw()
