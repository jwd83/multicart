import pygame
import random

class Deck():
    def __init__(self):
        self.deck: list[str] = ["basic", "fire"]

    def get_deck(self,):
        return self.deck.copy()

    def draw_from_deck(self,):
        return self.deck[random.randint(0, len(self.deck) - 1)]

