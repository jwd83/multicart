import pygame
from scene import Scene
from utils import *
from .scripts import blackjack as bj


class JackBlackJack(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.game_board = load_tpng("jackblackjack/game-board.png")

        self.deck = bj.Deck()
        self.hand_player = bj.Hand()
        self.hand_dealer = bj.Hand()

        self.new_game()

    def new_game(self):

        self.deck = bj.Deck()
        self.hand_player.empty()
        self.hand_dealer.empty()

        self.deck.shuffle()

        self.hand_player.add_card(self.deck.deal())
        self.hand_player.add_card(self.deck.deal())

        self.hand_dealer.add_card(self.deck.deal())
        self.hand_dealer.add_card(self.deck.deal())

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_replace = "Menu"

        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_replace = "JackBlackJack"

    def draw(self):
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.game_board, (0, 0))
