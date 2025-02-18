import pygame
from scene import Scene
from utils import *
from .scripts import blackjack as bj
from classes.button import Button
from enum import Enum, auto
import settings


## todo
# double down
# split
# insurance
# five card charlie


# blackjack hand strength
# -------------------------
# blackjack with ace and (10, J, Q, K) = 21 in 2 cards only!
# 5 card charlie = 5 cards without busting
# hands up to and including 21 are ranked by the sum of their cards
# bust = over 21


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

        self.mouse_hide = True

        self.deck = bj.Deck()
        self.hand_player = bj.Hand()
        self.hand_dealer = bj.Hand()

        self.game_board = load_tpng("jackblackjack/game-board.png")
        self.card_front = load_tpng("jackblackjack/card-blank-border.png")
        self.card_back = load_tpng("jackblackjack/card-back.png")
        self.suit_spades = load_tpng("jackblackjack/suit-spades.png")
        self.suit_hearts = load_tpng("jackblackjack/suit-hearts.png")
        self.suit_clubs = load_tpng("jackblackjack/suit-clubs.png")
        self.suit_diamonds = load_tpng("jackblackjack/suit-diamonds.png")

        self.new_game()

        self.selected = 0
        self.max_selected = 4

        self.state: GameState = GameState.TAKING_BETS

        self.bet_increment: int = 10
        self.bet: int = 10
        self.balance: int = 250

        button_width = 160
        button_height = 40
        button_font_size = 20
        button_font_size_large = 40

        left_col = (640 / 2) - button_width
        right_col = 640 / 2
        high_row = 0
        low_row = 40

        self.texts = {}

        self.update_texts()

        self.buttons = {
            "hit": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, high_row),
                size=(button_width, button_height * 2),
                content="Hit",
                fontSize=button_font_size_large,
                bg_color=(40, 120, 120),
            ),
            "stand": Button(
                screen=self.screen,
                scene=self,
                pos=(right_col, high_row),
                size=(button_width, button_height * 2),
                content="Stand",
                fontSize=button_font_size_large,
                bg_color=(120, 120, 40),
            ),
            "bet more": Button(
                screen=self.screen,
                scene=self,
                pos=(right_col, high_row),
                size=(button_width, button_height),
                content="Bet More",
                fontSize=button_font_size,
                bg_color=(100, 240, 100),
            ),
            "bet less": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, high_row),
                size=(button_width, button_height),
                content="Bet Less",
                fontSize=button_font_size,
                bg_color=(240, 100, 100),
            ),
            "deal": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, low_row),
                size=(button_width * 2, button_height),
                content="Deal",
                fontSize=button_font_size,
                bg_color=(100, 100, 240),
            ),
            "next hand": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, high_row),
                size=(button_width * 2, button_height * 2),
                content="next hand",
                fontSize=button_font_size_large,
                bg_color=(100, 240, 100),
            ),
            "juice deck": Button(
                screen=self.screen,
                scene=self,
                pos=(left_col, low_row * 2),
                size=(button_width * 2, button_height),
                content="Juice Deck",
                fontSize=button_font_size,
                bg_color=(240, 100, 100),
            ),
        }

    def update_texts(self):

        # check if texts have been defined
        if "dealer" in self.texts:
            if self.state == GameState.WAIT_NEXT_HAND:
                self.texts["dealer"].text = f"{self.hand_dealer.value()}"
            else:
                self.texts["dealer"].text = ""

            if self.hand_player.value() != 0:
                self.texts["player"].text = f"{self.hand_player.value()}"
            else:
                self.texts["player"].text = ""

            self.texts["balance"].text = f"balance: {self.balance}"
            self.texts["bet"].text = f"bet: {self.bet}"

            positive_sign = "+" if self.deck.running_count() > 0 else ""
            self.texts["count"].text = (
                f"rc:{positive_sign}{int(self.deck.running_count())}, dr: {self.deck.decks_remaining():.2f}, tc: {positive_sign}{self.deck.true_count():.1f}, cr: {self.deck.cards_remaining()}"
            )

        else:

            left_pos = 320
            y_base = -30
            y_step = 30

            self.standard_font_size = 20

            self.texts["bet"] = self.Text(f"bet: ?", (0, 0))
            self.texts["balance"] = self.Text(f"balance: 0", (0, 30))

            self.texts["winner"] = self.Text(f"", (left_pos, y_base + y_step * 7))
            self.texts["count"] = self.Text(f"", (0, 328))

            self.standard_font_size = 60

            self.texts["dealer"] = self.Text(
                " ",
                (0, 75),
            )
            self.texts["player"] = self.Text(
                " ",
                (0, 305),
            )

            self.standard_font_size = 20

    def new_game(self):

        self.deck.reset()
        self.hand_player.empty()
        self.hand_dealer.empty()

    def update_game_state(self):

        if self.state == GameState.NEW_GAME:

            self.deck.reset()
            self.hand_player.empty()
            self.hand_dealer.empty()

            self.balance = 250
            self.bet = self.bet_increment
            self.state = GameState.NEW_HAND

        if self.state == GameState.NEW_HAND:

            # empty hands
            self.hand_player.empty()
            self.hand_dealer.empty()

            # draw a new deck if the percentage of cards remaining is less than 25%
            if self.deck.draw_percentage() < 0.25:
                self.deck.reset()

            self.bet = self.bet_increment
            self.state = GameState.TAKING_BETS

        if self.state == GameState.DEALING:

            if self.deal_start + 1 < self.elapsed():
                self.log(f"Finished dealing at {self.elapsed() - self.deal_start}")
                self.hand_player.add_card(self.deck.draw())
                self.hand_dealer.add_card(self.deck.draw())

                self.hand_player.add_card(self.deck.draw())
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
                # check for player having five card charlie
                if self.hand_player.hand_strength() == 30:
                    if self.hand_dealer.hand_strength() == 40:
                        self.state = GameState.DEALER_WIN
                        self.texts["winner"].text = "Blackjack beats charlie!"
                    else:
                        self.state = GameState.PLAYER_WIN
                        self.texts["winner"].text = "Five Card Charlie!"
                else:

                    while self.hand_dealer.value() < 17:
                        self.hand_dealer.add_card(self.deck.draw())

                    self.log(f"dealer hand strength: {self.hand_dealer.value()} ")
                    self.log(f"player hand strength: {self.hand_player.value()} ")

                    if self.hand_dealer.is_bust():
                        self.state = GameState.PLAYER_WIN
                        self.texts["winner"].text = "Player wins! The dealer busts! "

                    elif (
                        self.hand_player.hand_strength()
                        > self.hand_dealer.hand_strength()
                    ):
                        self.texts["winner"].text = "Player wins!"

                        self.state = GameState.PLAYER_WIN

                    elif (
                        self.hand_player.hand_strength()
                        < self.hand_dealer.hand_strength()
                    ):

                        self.texts["winner"].text = "Dealer wins!"
                        self.state = GameState.DEALER_WIN

                    else:
                        self.state = GameState.TIE
                        self.texts["winner"].text = "Tie!"

        if self.state == GameState.PLAYER_WIN:
            self.play_sound("cute-level-up-3-189853")

            # check if the player had blackjack for 3:2 payout
            if self.hand_player.hand_strength() == 40:
                self.balance += int(self.bet * 1.5)
            else:
                if self.hand_player.hand_strength() == 30:
                    self.balance += int(self.bet * 1.2)
                else:
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
        dealer_top = 100
        player_top = 210

        # DRAW THE PLAYERS HAND
        for i, card in enumerate(self.hand_player.cards):
            self.draw_card(card, 50 + i * card_spacing, player_top)

        # draw the dealer's hand
        for i, card in enumerate(self.hand_dealer.cards):
            if i == 0 and self.state == GameState.PLAYER_TURN:
                self.screen.blit(self.card_back, (50 + i * card_spacing, dealer_top))
            else:
                self.draw_card(card, 50 + i * card_spacing, dealer_top)

    def draw(self):
        # self.screen.fill((20, 120, 20))

        self.screen.blit(self.game_board, (0, 0))

        # draw the shoe/deck of cards we are drawing from, 1 pixel per 10 cards
        for i in range(self.deck.cards_remaining() // 10):
            self.screen.blit(self.card_back, (640 - 80 - i // 3, 50 - i))

        self.draw_hands()
        self.update_texts()

        if self.state == GameState.TAKING_BETS:
            bet_more: bool = self.buttons["bet more"].draw()
            bet_less: bool = self.buttons["bet less"].draw()
            deal: bool = self.buttons["deal"].draw()

        if self.state == GameState.PLAYER_TURN:
            hit: bool = self.buttons["hit"].draw()
            stand: bool = self.buttons["stand"].draw()

        if self.state == GameState.WAIT_NEXT_HAND:
            next_hand: bool = self.buttons["next hand"].draw()

        if self.buttons["juice deck"].draw():
            # add a full set of 10,j,q,k for each suit into the deck then shuffle it
            self.deck.juice()

        self.draw_text()

        if self.state == GameState.DEALING:
            if self.deal_start + 0.25 > self.elapsed():
                # slide 4 cards out from the top of the deck
                start_pos = (
                    640 - 80 - (self.deck.cards_remaining() // 10) // 3,
                    50 - (self.deck.cards_remaining() // 10),
                )

                for i in range(4):
                    self.screen.blit(
                        self.card_back,
                        (
                            start_pos[0] + i * (self.elapsed() - self.deal_start) * 160,
                            start_pos[1],
                        ),
                    )
            else:

                card_spacing = 80
                dealer_top = 100
                player_top = 210
                card_1 = 50
                card_2 = 50 + card_spacing

                progress = self.elapsed() - self.deal_start
                remaining = 1 - progress

                self.screen.blit(
                    self.card_back,
                    (card_1 + max(0, remaining - 0.3) * 2200, dealer_top),
                )
                self.screen.blit(
                    self.card_back,
                    (card_2 + max(0, remaining - 0.1) * 2200, dealer_top),
                )
                self.screen.blit(
                    self.card_back,
                    (card_1 + max(0, remaining - 0.4) * 2200, player_top),
                )
                self.screen.blit(
                    self.card_back,
                    (card_2 + max(0, remaining - 0.2) * 2200, player_top),
                )

        if self.state == GameState.PLAYER_TURN:

            if hit:
                self.hand_player.add_card(self.deck.draw())
                if self.hand_player.is_bust():
                    self.state = GameState.DEALER_TURN

                if len(self.hand_player.cards) == 5:
                    self.state = GameState.DEALER_TURN

            if stand:
                self.state = GameState.DEALER_TURN

        if self.state == GameState.TAKING_BETS:

            if bet_more:
                self.bet = max(
                    self.bet_increment, min(self.balance, self.bet + self.bet_increment)
                )

            if bet_less:
                self.bet = max(self.bet_increment, self.bet - self.bet_increment)

            if deal:
                self.deal_start = self.elapsed()
                self.state = GameState.DEALING

        if self.state == GameState.WAIT_NEXT_HAND:

            if next_hand:
                self.texts["winner"].text = ""
                self.state = GameState.NEW_HAND

        self.draw_mouse()
