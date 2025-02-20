from enum import Enum
import random


class Suit(Enum):
    """Enum for card suits"""

    HEARTS = 1
    DIAMONDS = 2
    CLUBS = 3
    SPADES = 4


class Rank(Enum):
    """Enum for card ranks"""

    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank.name} of {self.suit.name}"

    def value(self):
        if self.rank in [Rank.KING, Rank.QUEEN, Rank.JACK]:
            return 10
        if self.rank == Rank.ACE:
            return 11
        return self.rank.value


class Deck:
    def __init__(self, decks: int = 6):
        self.cards = []
        self.decks = max(1, decks)
        self.reset()

    def reset(self):
        self.decks = max(1, self.decks)
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank] * self.decks
        self.shuffle()

    def __str__(self):
        return "\n".join([str(card) for card in self.cards])

    def shuffle(self):
        random.shuffle(self.cards)

    def cards_remaining(self):
        return len(self.cards)

    def juice(self):
        # add a little extra juice to the deck
        extras = [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]
        for extra in extras:
            self.cards.append(Card(Suit.HEARTS, extra))
            self.cards.append(Card(Suit.DIAMONDS, extra))
            self.cards.append(Card(Suit.CLUBS, extra))
            self.cards.append(Card(Suit.SPADES, extra))

        self.shuffle()

    def draw(self):

        card_out = None
        if len(self.cards):
            card_out = self.cards.pop()

            # check if this was the last card
            if len(self.cards) == 0:
                self.reset()

        else:
            self.reset()
            card_out = self.cards.pop()

        return card_out

    def running_count(self):
        running_count = 0
        for card in self.cards:
            if card.rank in [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING, Rank.ACE]:
                running_count += 1
            elif card.rank in [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX]:
                running_count -= 1

        return running_count

    def decks_remaining(self):
        return len(self.cards) / 52

    def draw_percentage(self):
        return self.cards_remaining() / (52 * self.decks)

    def true_count(self):

        return self.running_count() / self.decks_remaining()


class Hand:
    def __init__(self):
        self.cards = []

    def __str__(self):
        return "\n".join([str(card) for card in self.cards])

    def empty(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def value(self):
        value = sum([card.value() for card in self.cards])
        num_aces = sum([1 for card in self.cards if card.rank == Rank.ACE])
        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1
        return value

    def minimum_value(self):
        # like value but all aces are worth 1
        value = sum([card.value() for card in self.cards])
        num_aces = sum([1 for card in self.cards if card.rank == Rank.ACE])
        while num_aces:
            value -= 10
            num_aces -= 1
        return value

    def is_bust(self):
        return self.value() > 21

    def dealer_showing(self):
        return self.cards[1]

    def hand_strength(self):
        # natural blackjack = 40
        # five card charlie = 30
        # hand sum = 4-21
        # bust = -1

        # look for perfect blackjack
        if self.value() == 21 and len(self.cards) == 2:
            return 40

        # look for five card charlie
        if self.minimum_value() <= 21 and len(self.cards) == 5:
            return 30

        # look for busted hand
        if self.is_bust():
            return -1

        # default to hand sum if none of the above match
        return self.value()


if __name__ == "__main__":
    # creating a card
    # print("Creating a test card: ace of hearts")
    # test_card = Card(Suit.HEARTS, Rank.ACE)
    # print(test_card)

    # creating a deck
    print("Creating a test deck")
    test_deck = Deck(3)
    print(f"Cards remaining: {test_deck.cards_remaining()}")
    print(test_deck)

    # give the dealer a hand
    dealer_hand = Hand()
    dealer_hand.add_card(test_deck.draw())
    dealer_hand.add_card(test_deck.draw())

    # give the player a hand
    player_hand = Hand()
    player_hand.add_card(test_deck.draw())
    player_hand.add_card(test_deck.draw())

    print("Dealer's hand:")
    print(
        str(dealer_hand.dealer_showing()) + f"({dealer_hand.dealer_showing().value()})"
    )
    print("Player's hand:")
    print(player_hand)
    print("Player's hand value:" + str(player_hand.value()))

    # player's turn
    while player_hand.value() < 21:
        hit = input("Do you want to hit? (y/n)")
        if hit == "y":
            next_card = test_deck.draw()
            print("You drew a " + str(next_card))
            player_hand.add_card(next_card)
            print("Player's hand:")
            print(player_hand)
            print("Player's hand value:" + str(player_hand.value()))
        else:
            break

    if player_hand.is_bust():
        print("Player busts!")

    # dealer's turn
    print("Dealer reveals their hand:")
    print(dealer_hand)
    while dealer_hand.value() < 17:
        print("Dealer hits and draws a...")
        next_card = test_deck.draw()
        print(next_card)
        dealer_hand.add_card(next_card)
        print("Dealer's hand now worth:" + str(dealer_hand.value()))

    if dealer_hand.is_bust():
        print("Dealer busts!")

    print("Dealer's hand value:" + str(dealer_hand.value()))
    print("Player's hand value:" + str(player_hand.value()))

    # determine the winner

    # dealer wins if they both bust
    if player_hand.is_bust():
        print("Dealer wins!")

    # player wins if only the dealer busts
    elif dealer_hand.is_bust():
        print("Player wins!")

    # if neither busts, the higher value wins
    elif player_hand.value() > dealer_hand.value():
        print("Player wins!")
    elif player_hand.value() < dealer_hand.value():
        print("Dealer wins!")
    # it's a tie otherwise
    else:
        print("It's a tie!")
