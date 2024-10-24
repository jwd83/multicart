import pygame
from scene import Scene
from utils import *
from .scripts import blackjack as bj
from classes.button import Button
from enum import Enum, auto
import settings


class GameState(Enum):
    NEW_GAME = auto()
    NEW_HAND = auto()
    TAKING_BETS = auto()
    DEALING = auto()
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    PLAYER_WIN = auto()
    DEALER_WIN = auto()
    TIE = auto()
    WAIT_NEXT_HAND = auto()


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

        self.bet: int = 1
        self.balance: int = 25

        button_width = 160
        button_height = 40
        button_font_size = 30
        left_col = 0
        middle_col = button_width
        right_col = button_width * 2
        high_row = 0
        low_row = 40

        self.texts = {}

        self.update_texts()

        self.buttons = {
            "hit": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, low_row),
                size=(button_width, button_height),
                content="Hit",
                fontSize=button_font_size,
            ),
            "stand": Button(
                screen=self.screen,
                scene=self,
                pos=(middle_col, low_row),
                size=(button_width, button_height),
                content="Stand",
                fontSize=button_font_size,
            ),
            "bet more": Button(
                screen=self.screen,
                scene=self,
                pos=(middle_col, high_row),
                size=(button_width, button_height),
                content="Bet More",
                fontSize=button_font_size,
            ),
            "bet less": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, high_row),
                size=(button_width, button_height),
                content="Bet Less",
                fontSize=button_font_size,
            ),
            "deal": Button(
                screen=self.screen,
                scene=self,
                pos=(right_col, high_row),
                size=(button_width, button_height),
                content="Deal",
                fontSize=button_font_size,
            ),
            "next hand": Button(
                screen=self.screen,
                scene=self,
                pos=(right_col, low_row),
                size=(button_width, button_height),
                content="next hand",
                fontSize=button_font_size,
            ),
        }

    def update_texts(self):

        # check if texts have been defined
        if "dealer" in self.texts:
            if self.state == GameState.PLAYER_TURN:
                self.texts["dealer"].text = f"dealer has ?"
            else:
                self.texts["dealer"].text = f"dealer has {self.hand_dealer.value()}"

            self.texts["player"].text = f"player has {self.hand_player.value()}"
            self.texts["balance"].text = f"balance: {self.balance}"
            self.texts["bet"].text = f"bet: {self.bet}"
            self.texts["state"].text = self.state.name

        else:

            left_pos = 320
            y_base = 0
            y_step = 30

            self.texts["dealer"] = self.Text(
                " ",
                (0, 85),
            )
            self.texts["player"] = self.Text(
                " ",
                (0, 320),
            )
            self.texts["balance"] = self.Text(
                f"balance: ?", (left_pos, y_base + y_step * 4)
            )
            self.texts["bet"] = self.Text(f"bet: ?", (left_pos, y_base + y_step * 5))

            self.texts["state"] = self.Text(
                f"state: ?", (left_pos, y_base + y_step * 6)
            )
            self.texts["winner"] = self.Text(f"", (left_pos, y_base + y_step * 7))

    def new_game(self):

        self.deck.reset()
        self.hand_player.empty()
        self.hand_dealer.empty()

    def update_game_state(self):

        if self.state == GameState.NEW_GAME:

            self.deck.reset()
            self.hand_player.empty()
            self.hand_dealer.empty()

            self.balance = 25
            self.bet = 1
            self.state = GameState.TAKING_BETS

        if self.state == GameState.NEW_HAND:

            self.hand_player.empty()
            self.hand_dealer.empty()

            self.bet = 1
            self.state = GameState.TAKING_BETS

        if self.state == GameState.DEALING:

            self.hand_player.add_card(self.deck.draw())
            self.hand_player.add_card(self.deck.draw())

            self.hand_dealer.add_card(self.deck.draw())
            self.hand_dealer.add_card(self.deck.draw())

            self.state = GameState.PLAYER_TURN

        if self.state == GameState.PLAYER_TURN:

            if self.hand_player.is_bust():
                self.state = GameState.DEALER_WIN

            elif self.hand_player.value() == 21:
                self.state = GameState.DEALER_TURN

        if self.state == GameState.DEALER_TURN:

            if self.hand_player.is_bust():
                self.state = GameState.DEALER_WIN
                self.texts["winner"].text = "Dealer wins! The player busts! "
            else:
                while self.hand_dealer.value() < 17:
                    self.hand_dealer.add_card(self.deck.draw())

                if self.hand_dealer.is_bust():
                    self.state = GameState.PLAYER_WIN
                    self.texts["winner"].text = "Player wins! The dealer busts! "

                elif self.hand_player.value() > self.hand_dealer.value():
                    self.texts["winner"].text = "Player wins!"

                    self.state = GameState.PLAYER_WIN

                elif self.hand_player.value() < self.hand_dealer.value():
                    self.texts["winner"].text = "Dealer wins!"
                    self.state = GameState.DEALER_WIN

                else:
                    self.state = GameState.TIE
                    self.texts["winner"].text = "Tie!"

        if self.state == GameState.PLAYER_WIN:
            self.balance += self.bet
            self.state = GameState.WAIT_NEXT_HAND

        if self.state == GameState.DEALER_WIN:
            self.balance -= self.bet
            self.state = GameState.WAIT_NEXT_HAND

        if self.state == GameState.TIE:
            self.state = GameState.WAIT_NEXT_HAND

    def update(self):
        # if the user presses escape or F5 key, quit the event loop.
        if pygame.K_ESCAPE in self.game.just_pressed:
            self.game.scene_replace = "Menu"

        if pygame.K_RETURN in self.game.just_pressed:
            self.game.scene_replace = "JackBlackJackTitle"

        self.update_game_state()

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

    def draw_hands(self):

        card_spacing = 80

        # DRAW THE PLAYERS HAND
        for i, card in enumerate(self.hand_player.cards):
            self.draw_card(card, 50 + i * card_spacing, 210)

        # draw the dealer's hand
        for i, card in enumerate(self.hand_dealer.cards):
            if i == 0 and self.state == GameState.PLAYER_TURN:
                self.screen.blit(self.card_back, (50 + i * card_spacing, 120))
            else:
                self.draw_card(card, 50 + i * card_spacing, 120)

    def draw(self):
        self.screen.fill((20, 120, 20))

        self.draw_hands()
        self.update_texts()

        hit: bool = self.buttons["hit"].draw()
        stand: bool = self.buttons["stand"].draw()
        bet_more: bool = self.buttons["bet more"].draw()
        bet_less: bool = self.buttons["bet less"].draw()
        deal: bool = self.buttons["deal"].draw()
        next_hand: bool = self.buttons["next hand"].draw()

        self.TextDraw()

        if self.state == GameState.PLAYER_TURN:

            if hit:
                self.hand_player.add_card(self.deck.draw())
                if self.hand_player.is_bust():
                    self.state = GameState.DEALER_TURN

            if stand:
                self.state = GameState.DEALER_TURN

        if self.state == GameState.TAKING_BETS:

            if bet_more:
                self.bet = max(1, min(self.balance, self.bet + 1))

            if bet_less:
                self.bet = max(1, self.bet - 1)

            if deal:
                self.state = GameState.DEALING

        if self.state == GameState.WAIT_NEXT_HAND:

            if next_hand:
                self.texts["winner"].text = ""
                self.state = GameState.NEW_HAND
