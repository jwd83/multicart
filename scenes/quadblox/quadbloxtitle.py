import pygame
from scene import Scene
from utils import *

class QuadBloxTitle(Scene):
    def __init__(self, game):
        super().__init__(game)

        # self.play_music("sounds/korobeiniki-arranged-for-piano-186249.mp3")
        # self.play_music("sounds/korobeiniki-rearranged-arr-for-strings-185592.mp3")
        self.play_music("sounds/korobeiniki-rearranged-arr-for-music-box-184978.mp3")

        self.background = load_tpng("quadblox/title.png")

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_replace = "QuadBlox"

    def draw(self):
        self.screen.blit(self.background, (0, 0))

