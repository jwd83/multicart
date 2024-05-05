import pygame
from scene import Scene
from utils import *

class QuadBloxTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.background = load_tpng("quadblox/title.png")

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_replace = "QuadBlox"

    def draw(self):
        self.screen.blit(self.background, (0, 0))

