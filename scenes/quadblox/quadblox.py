import pygame
from scene import Scene
from utils import *
from .scripts.qb import Board, colors

class QuadBlox(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.player = Board()

        print(self.player.grid)


    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_push = "Menu"

        if pygame.K_LEFT in self.game.just_pressed:
            for y, row in enumerate(self.player.grid):
                for x, cell in enumerate(row):
                    self.player.grid[y][x] = (self.player.grid[y][x] - 1) % len(colors)

        if pygame.K_RIGHT in self.game.just_pressed:
            for y, row in enumerate(self.player.grid):
                for x, cell in enumerate(row):
                    self.player.grid[y][x] = (self.player.grid[y][x] + 1) % len(colors)

        if pygame.K_UP in self.game.just_pressed:
            print(self.player)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.draw_board(self.player, (0, 0))

    def draw_board(self, board, pos, block_size = 16):

        for y, row in enumerate(self.player.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, colors[cell], (x * block_size, y * block_size, block_size - 1, block_size - 1))
