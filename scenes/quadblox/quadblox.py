from numpy import block
import pygame
from scene import Scene
from utils import *
from .scripts.qb import Board, colors

class QuadBlox(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.player = Board()

        self.opponents = [Board() for _ in range(8)]

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
        self.draw_board(self.player, (100, 10))

        opponent_block_size = 6

        x_step = opponent_block_size * 11

        y1 = 10
        y2 = y1 + 28 * opponent_block_size

        x = 640 / 2
        y = y1

        for i, opponent in enumerate(self.opponents):
  
            self.draw_board(opponent, (x, y), opponent_block_size)

            if i % 2 == 0:
                y = y2
            else:
                y = y1
                x += x_step          

    def draw_board(self, board: Board, pos, block_size = 12):

        # draw a red horizontal line after the first 4 rows        
        pygame.draw.line(
            self.screen, 
            (255, 0, 0), 
            (pos[0], pos[1] + 4 * block_size-1), 
            (pos[0] + 10 * block_size -1, pos[1] + 4 * block_size -1)
        )

        for y, row in enumerate(board.grid):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen, 
                        colors[cell], 
                        (
                            pos[0] + x * block_size, 
                            pos[1] + y * block_size, 
                            block_size - 1, 
                            block_size - 1)
                    )
