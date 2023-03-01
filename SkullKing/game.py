from typing import List
import random

#################################### Card objects ####################################

class Card:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.bonus_points = 0
        self.trick_order = 0

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] {self.name}"

    def __repr__(self) -> str:
        return f"[{self.__class__.__name__}] {self.name}"

CARD_COLOR_BLACK = 0
CARD_COLOR_YELLOW = 1
CARD_COLOR_GREEN = 2
CARD_COLOR_PINK = 3

class Number(Card):
    def __init__(self, id, name, color, value):
        super().__init__(id, name)
        self.color = color
        self.value = value

        # Assign bonus points for 14 cards
        if value == 14:
            self.bonus_points = 20 if color == CARD_COLOR_BLACK else 10

    def __gt__(self, other, trump_color):
        super().__gt__(other)

class Pirate(Card):
    def capture_mermaid(self, count):
        self.bonus_points += count*20

class Mermaid(Card):
    def capture_skullking(self):
        self.bonus_points = 50

class SkullKing(Card):
    def capture_pirate(self, count):
        self.bonus_points += count*30

class Escape(Card):
    pass

class Loot(Card):
    pass

class Kraken(Card):
    pass

class WhiteWhale(Card):
    pass

class Tigress(Card):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.as_pirate = True

    def use_as_pirate(self, as_pirate):
        self.as_pirate = as_pirate

ALL_CARDS = [
    SkullKing(0, "Skull King"),
    Pirate(1, "Harry the Giant"),
    Pirate(2, "Juanita Jade"),
    Pirate(3, "Rascal of Roatan"),
    Pirate(4, "Rosie de Lancy"),
    Pirate(5, "Bahij the Bandit"),
    Mermaid(6, "Sirena"),
    Mermaid(7, "Alyra"),
    Kraken(8, "Kraken"),
    Escape(9, "Escape"),
    Escape(10, "Escape"),
    Escape(11, "Escape"),
    Escape(12, "Escape"),
    Loot(13, "Loot"),
    Loot(14, "Loot"),
    WhiteWhale(15, "White Whale"),
    Tigress(16, "Tigress")
]

id = len(ALL_CARDS)
for color in [CARD_COLOR_BLACK, CARD_COLOR_YELLOW, CARD_COLOR_GREEN, CARD_COLOR_PINK]:
    for i in range(1, 15):
        if color == CARD_COLOR_BLACK:
            color_name = "black"
        elif color == CARD_COLOR_YELLOW:
            color_name = "yellow"
        elif color == CARD_COLOR_GREEN:
            color_name = "green"
        elif color == CARD_COLOR_PINK:
            color_name = "pink"
        ALL_CARDS.append(Number(id, f"{color_name} {i}", color, i))
        id += 1

#################################### Non-card objects ####################################

class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def __len__(self):
        return len(self.cards)

    def add_card(self, card):
        self.cards.append(card)

    def add_cards(self, cards):
        self.cards += cards

    def pick(self, name):
        for i, card in enumerate(self.cards):
            if card.name == name:
                self.cards.pop(i)
                return card


class Deck:
    def __init__(self):
        self.cards: List[Card] = []

        self.reset()

    def __len__(self):
        return len(self.cards)

    def reset(self):
        self.cards = ALL_CARDS.copy()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n_cards):
        drawn_cards = []
        for _ in range(n_cards):
            drawn_cards.append(self.cards.pop())
        return drawn_cards

class Trick:
    def __init__(self) -> None:
        self.cards: List[Card] = []
        self.color = None

    @property
    def bonus_points(self) -> float:
        bonus_points = 0
        for card in self.cards:
            bonus_points += card.bonus_points

        return bonus_points

    def add_card(self, player_id: int, card: Card):
        self.cards.append((player_id, card))

        if self.color is None and isinstance(card, Number):
            self.color = card.color

    def get_trump_color(self):
        return self.color

    def get_winner(self):
        """Compute the id of the player who won the trick"""
        current_winner = 0
        current_winning_card = None
        trump_color = ""

        for player_id, card in self.cards:
            pass
