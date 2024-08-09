import pygame
from scene import Scene
import random
import settings
from copy import deepcopy

from scenes.jackdefense.scripts.util import Deck
from utils import Button

class JackDefenseGameBoard(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.background = pygame.surface.Surface(self.screen.get_size())

        self.deck = Deck()

        self.draw_button = Button(self.background, pos = (self.screen.get_size()[0] // 2, (self.screen.get_size()[1] // 1.4)), size = (100, 100), content = "Draw")

    def update(self):
        self.background.fill((80, 80, 80))
        if self.draw_button.draw(): 
            print(self.deck.draw_from_deck())

    def draw(self):
        self.game.screen.fill((80, 80, 80))
        self.screen.blit(self.background, (0, 0))

