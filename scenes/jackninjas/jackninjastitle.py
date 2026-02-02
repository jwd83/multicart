import pygame
from scene import Scene
from utils import *


class JackNinjasTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.title_image = load_tpng("jackninjas/jack-ninjas-title-360p.png")

    def update(self):
        if self.game.input["cancel"].just_pressed:
            self.game.scene_replace = "Menu"

        if self.game.input["confirm"].just_pressed:
            self.game.scene_replace = "JackNinjas"

    def draw(self):
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.title_image, (0, 0))
