import pygame
import random
from scene import Scene
from utils import *

class Deck():
    def __init__(self):
        self.deck: list[str] = ["basic", "fire"]

    def get_deck(self,):
        return self.deck.copy()

    def draw_from_deck(self,):
        return random.choices(self.deck)

class Enemy(pygame.sprite.Sprite, Scene):
    def __init__(self, game, e_type, path):
        super().__init__(game)
        pygame.sprite.Sprite.__init__()
        
        self.image, self.rect = self.load_png("opengameart-jeton-bleu.png")

        self.image = pygame.transform.scale(self.image, (8, 8))
        self.rect = self.image.get_rect()

        self.path = path
        self.pos = path[0]["pos"]

        # direction is represented as a tuple (x_dir, y_dir)
        # and will be 0 for no change, 1 or -1 for change
        self.direction: tuple[int, int] = path[1]["direction"]
        self.moving_to: tuple[int, int] = path[1]["pos"]

        self.health: int = 0
        self.speed: int = 0

        match e_type:
            case "basic":
                self.health = 1000
                self.speed = 5
                print('Initializing basic enemy')

    def update(self):
        # check for collision with bullets

        # update our movement
        dx = 0
        dy = 0 
        new_rect = self.rect.copy()

        # confirm we're not moving past our target in the x direction
        if abs(new_rect.x + dx) < abs(self.moving_to[0]):
            dx = self.direction[0] * self.speed
        else: dx = self.moving_to[0] - new_rect.x

        # and again for y
        if abs(new_rect.y + dy) < abs(self.moving_to[1]):
            dy = self.direction[1] * self.speed
        else: dy = self.moving_to[1] - new_rect.y

        # and finally move our sprite
        new_rect.x += dx
        new_rect.y += dy
        self.rect = new_rect

        # check for collision with end
        if self.rect.collidepoint(self.moving_to):
            print('Enemy reached end!')
            pygame.sprite.Sprite.kill(self)
