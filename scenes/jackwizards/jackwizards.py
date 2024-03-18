# this file is just for reference, it is not used in the game

import pygame
from scene import Scene

class JackWizards(Scene):
    def __init__(self, game):
        super().__init__(game)

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

    def draw(self):
        self.screen.fill((0, 0, 0))
