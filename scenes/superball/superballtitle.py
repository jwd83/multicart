# this file is just for reference, it is not used in the game

import pygame
from scene import Scene

class SuperBallTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.background, _ = self.load_png("dalle-superball.png")

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_replace = "SuperBallField"

    def draw(self):
        self.screen.blit(self.background, (0, 0))
