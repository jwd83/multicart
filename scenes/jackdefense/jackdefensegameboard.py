import pygame
from scene import Scene
import random
import settings
from copy import deepcopy

from scenes.jackdefense.scripts.util import Deck
from utils import Button, draw_grid

class JackDefenseGameBoard(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tile_size = 8
        self.tile_grid = {}
        self.background = pygame.surface.Surface(self.screen.get_size())
        
        self.deck = Deck()

        self.create_enemy_path()
        print(self.tile_grid)
        

    # creates a straight horizontal enemy path along the grid
    def create_enemy_path(self, start_pos = (0, 4)):
        img: pygame.surface.Surface = pygame.surface.Surface((self.tile_size, self.tile_size))
        img.fill((0, 0, 20))
        for i in range(start_pos[0], self.background.get_width() // self.tile_size):
            self.tile_grid[f'{i};{start_pos[1]}'] = {
                "type": "path",
                "img": img,
                "pos": (i * self.tile_size, start_pos[1] * self.tile_size)
                }


    def update(self):
        self.background.fill((80, 80, 80))

        for key in self.tile_grid:

            self.background.blit(self.tile_grid[key]["img"], self.tile_grid[key]["pos"])

        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "GameSelect"

    def draw(self):
        self.screen.blit(self.background, (0, 0))
