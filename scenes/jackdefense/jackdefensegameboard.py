import pygame
from scene import Scene
import random
import settings
from copy import deepcopy

from scenes.jackdefense.scripts.util import Deck, Enemy
from utils import Button, draw_grid

class JackDefenseGameBoard(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.tile_size = 8
        self.tile_grid = {}
        self.background = pygame.surface.Surface(self.screen.get_size())
        
        self.deck = Deck()

        self.path = self.create_enemy_path()
        self.enemy_list = {
            "basic": {
                "total_count": 20,
                "remaining": 20, 
                "spawn_delay": 90,
                "spawn_cd": 90, # frames between spawns 
                "frame_count": 0
            }
        }
        self.enemy_group = pygame.sprite.Group()
        print(self.tile_grid)
        

    # creates a straight horizontal enemy path along the grid
    def create_enemy_path(self, start_pos = (0, 4)):
        path = []
        img: pygame.surface.Surface = pygame.surface.Surface((self.tile_size, self.tile_size))
        img.fill((0, 0, 20))
        for i in range(start_pos[0], self.background.get_width() // self.tile_size):
            piece = {
                "type": "path",
                "img": img,
                "pos": (i * self.tile_size, start_pos[1] * self.tile_size),
                "direction": (1, 0),
                }
            self.tile_grid[f'{i};{start_pos[1]}'] = piece
            path.append(piece)
            return path


    def update(self):
        self.background.fill((80, 80, 80))

        for key in self.tile_grid:
            self.background.blit(self.tile_grid[key]["img"], self.tile_grid[key]["pos"])

        for e_type in self.enemy_list: 
            e = self.enemy_list[e_type]
            
            if (e["total_count"] == e["remaining"] and e["frame_count"] >= e["spawn_delay"]) or (e["total_count"] != e["remaining"] and e["frame_count"] >= e["spawn_cd"]):
                self.enemy_list[e_type]["frame_count"] = 0
                self.enemy_group.add(Enemy(self.game, "basic", self.path))
            else: self.enemy_list[e_type]["frame_count"] += 1

        self.enemy_group.update()
        self.enemy_group.draw(self.background)

        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "GameSelect"

    def draw(self):
        self.screen.blit(self.background, (0, 0))
