import pygame
from scene import Scene
from utils import *
from .scripts import blackjack as bj

from enum import Enum


class GameState(Enum):
    TAKING_BETS = 0
    PLAYER_TURN = 1
    DEALER_TURN = 2
    PLAYER_WIN = 3
    DEALER_WIN = 4
    TIE = 5


class JackBlackJack(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.deck = bj.Deck()
        self.hand_player = bj.Hand()
        self.hand_dealer = bj.Hand()

        self.card_front = load_tpng("jackblackjack/card-blank-border.png")
        self.card_back = load_tpng("jackblackjack/card-back.png")
        self.suit_spades = load_tpng("jackblackjack/spades.png")
        self.suit_hearts = load_tpng("jackblackjack/hearts.png")
        self.suit_clubs = load_tpng("jackblackjack/clubs.png")
        self.suit_diamonds = load_tpng("jackblackjack/diamonds.png")

        self.new_game()

        self.selected = 0
        self.max_selected = 4

        self.state: GameState = GameState.TAKING_BETS

    def new_game(self):

        self.deck.reset()
        self.hand_player.empty()
        self.hand_dealer.empty()

        self.hand_player.add_card(self.deck.draw())
        self.hand_player.add_card(self.deck.draw())

        self.hand_dealer.add_card(self.deck.draw())
        self.hand_dealer.add_card(self.deck.draw())

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_replace = "Menu"

        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_replace = "JackBlackJackTitle"

    def draw_card(self, card: bj.Card, x: int, y: int):

        self.screen.blit(self.card_front, (x, y))
        # draw the card's rank and suit

        if card.suit in [bj.Suit.DIAMONDS, bj.Suit.HEARTS]:
            card_color = (255, 0, 0)
        else:
            card_color = (0, 0, 0)

        if card.value() == 10 or card.value() == 11:
            if card.value() == 11:
                card_text = "A"
            if card.rank == bj.Rank.KING:
                card_text = "K"
            if card.rank == bj.Rank.QUEEN:
                card_text = "Q"
            if card.rank == bj.Rank.JACK:
                card_text = "J"
            if card.rank == bj.Rank.TEN:
                card_text = "10"
        else:
            card_text = str(card.value())

        card_text_image = self.make_text(card_text, card_color, 40)

        if card.suit == bj.Suit.SPADES:
            icon = self.suit_spades
        elif card.suit == bj.Suit.HEARTS:
            icon = self.suit_hearts
        elif card.suit == bj.Suit.CLUBS:
            icon = self.suit_clubs
        else:
            icon = self.suit_diamonds

        self.screen.blit(card_text_image, (x + 10, y + 10))
        self.screen.blit(icon, (x + 10, y + 50))

    def draw(self):
        self.screen.fill((20, 120, 20))

        # DRAW THE PLAYERS HAND
        for i, card in enumerate(self.hand_player.cards):
            self.draw_card(card, 50 + i * 120, 200)

        # draw the dealer's hand
        for i, card in enumerate(self.hand_dealer.cards):
            if i == 0:
                self.screen.blit(self.card_back, (50 + i * 120, 50))
            else:
                self.draw_card(card, 50 + i * 120, 50)
