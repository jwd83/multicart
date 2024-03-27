# this file is just for reference, it is not used in the game

import pygame
from scene import Scene
from utils import *

class JackWizardsMap(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.map_image = load_tpng("jackwizards/dall-e-map.png")

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_TAB in self.game.just_pressed:
            self.game.scene_pop = True

    def draw(self):
        # self.screen.fill((0, 0, 0))

        # draw the map image at the center of the screen
        x = (self.screen.get_width() - self.map_image.get_width()) // 2
        y = (self.screen.get_height() - self.map_image.get_height()) // 2
        self.screen.blit(self.map_image, (x, y))
