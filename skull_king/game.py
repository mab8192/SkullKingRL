import copy
import random
from typing import List, Tuple

#################################### Card objects ####################################

class Card:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.bonus_points = 0
        self.trick_order = 0

    def __str__(self) -> str:
        return f"({self.id})[{self.__class__.__name__}] {self.name}"

    def __repr__(self) -> str:
        return f"({self.id})[{self.__class__.__name__}] {self.name}"

    def __gt__(self, other):
        if not isinstance(other, Card): raise ValueError

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

    def __gt__(self, other, trick_color):
        super().__gt__(other)
        if isinstance(other, Number):
            if self.color == CARD_COLOR_BLACK and other.color != CARD_COLOR_BLACK:
                return True
            elif self.color != CARD_COLOR_BLACK and other.color == CARD_COLOR_BLACK:
                return False
            elif self.color == trick_color and other.color != trick_color:
                return True
            elif self.color != trick_color and other.color == trick_color:
                return False
            else:
                return self.value > other.value
        elif isinstance(other, Pirate):
            return False
        elif isinstance(other, Mermaid):
            return False
        elif isinstance(other, SkullKing):
            return False
        elif isinstance(other, Escape) or isinstance(other, Loot):
            return True
        elif isinstance(other, Kraken):
            return True
        elif isinstance(other, WhiteWhale):
            return True
        elif isinstance(other, Tigress):
            return False if other.as_pirate else True
        else:
            raise NotImplementedError

class Pirate(Card):
    def capture_mermaids(self, count):
        self.bonus_points += count*20

    def __gt__(self, other):
        super().__gt__(other)
        if isinstance(other, Number):
            return True
        elif isinstance(other, Pirate):
            return self.trick_order < other.trick_order
        elif isinstance(other, Mermaid):
            return not other.captured_sk  # Pirate beats mermaid unless she captured the skull king
        elif isinstance(other, SkullKing):
            return False
        elif isinstance(other, Escape) or isinstance(other, Loot):
            return True
        elif isinstance(other, Kraken):
            return True
        elif isinstance(other, WhiteWhale):
            return self.trick_order < other.trick_order
        elif isinstance(other, Tigress):
            if other.as_pirate:
                return self.trick_order < other.trick_order
            else:
                return True
        else:
            raise NotImplementedError

class Mermaid(Card):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.captured_sk = False

    def capture_skullking(self):
        self.bonus_points = 50
        self.captured_sk = True

    def __gt__(self, other):
        super().__gt__(other)
        if isinstance(other, Number):
            return True
        elif isinstance(other, Pirate):
            return self.captured_sk  # Mermaid beats pirate if it captured the skull king
        elif isinstance(other, Mermaid):
            return self.trick_order < other.trick_order
        elif isinstance(other, SkullKing):
            return True
        elif isinstance(other, Escape) or isinstance(other, Loot):
            return True
        elif isinstance(other, Kraken):
            return True
        elif isinstance(other, WhiteWhale):
            return self.trick_order < other.trick_order
        elif isinstance(other, Tigress):
            if other.as_pirate:
                return False
            else:
                return True
        else:
            raise NotImplementedError

class SkullKing(Card):
    def capture_pirates(self, count):
        self.bonus_points += count*30

    def __gt__(self, other):
        super().__gt__(other)
        if isinstance(other, Number):
            return True
        elif isinstance(other, Pirate):
            return True
        elif isinstance(other, Mermaid):
            return False
        elif isinstance(other, SkullKing):
            raise RuntimeError("Cannot compare two skull king cards")
        elif isinstance(other, Escape) or isinstance(other, Loot):
            return True
        elif isinstance(other, Kraken):
            return True
        elif isinstance(other, WhiteWhale):
            return self.trick_order < other.trick_order
        elif isinstance(other, Tigress):
            return True
        else:
            raise NotImplementedError

class Escape(Card):
    def __gt__(self, other):
        super().__gt__(other)
        if isinstance(other, Number):
            return False
        elif isinstance(other, Pirate):
            return False
        elif isinstance(other, Mermaid):
            return False
        elif isinstance(other, SkullKing):
            return False
        elif isinstance(other, Escape) or isinstance(other, Loot):
            return self.trick_order < other.trick_order
        elif isinstance(other, Kraken):
            return self.trick_order < other.trick_order
        elif isinstance(other, WhiteWhale):
            return self.trick_order < other.trick_order
        elif isinstance(other, Tigress):
            if other.as_pirate:
                return False
            else:
                return self.trick_order < other.trick_order
        else:
            raise NotImplementedError

class Loot(Card):
    def __gt__(self, other):
        super().__gt__(other)
        if isinstance(other, Number):
            return False
        elif isinstance(other, Pirate):
            return False
        elif isinstance(other, Mermaid):
            return False
        elif isinstance(other, SkullKing):
            return False
        elif isinstance(other, Escape) or isinstance(other, Loot):
            return self.trick_order < other.trick_order
        elif isinstance(other, Kraken):
            return self.trick_order < other.trick_order
        elif isinstance(other, WhiteWhale):
            return self.trick_order < other.trick_order
        elif isinstance(other, Tigress):
            if other.as_pirate:
                return False
            else:
                return self.trick_order < other.trick_order
        else:
            raise NotImplementedError

class Kraken(Card):
    def __gt__(self, other):
        super().__gt__(other)
        return False

class WhiteWhale(Card):
    def __gt__(self, other):
        super().__gt__(other)
        return False

class Tigress(Card):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.as_pirate = True

    def use_as_pirate(self, as_pirate):
        self.as_pirate = as_pirate

    def __gt__(self, other):
        super().__gt__(other)
        if isinstance(other, Number):
            return True if self.as_pirate else False
        elif isinstance(other, Pirate):
            return True if self.as_pirate and self.trick_order < other.trick_order else False
        elif isinstance(other, Mermaid):
            return True if self.as_pirate else False
        elif isinstance(other, SkullKing):
            return False
        elif isinstance(other, Escape) or isinstance(other, Loot):
            if self.as_pirate:
                return True
            else:
                return self.trick_order < other.trick_order
        elif isinstance(other, Kraken):
            return True
        elif isinstance(other, WhiteWhale):
            return self.trick_order < other.trick_order
        elif isinstance(other, Tigress):
            raise RuntimeError("Cannot compare two Tigresses")
        else:
            raise NotImplementedError

ALL_CARDS: List[Card] = [
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
            color_name = "Black"
        elif color == CARD_COLOR_YELLOW:
            color_name = "Yellow"
        elif color == CARD_COLOR_GREEN:
            color_name = "Green"
        elif color == CARD_COLOR_PINK:
            color_name = "Pink"
        ALL_CARDS.append(Number(id, f"{color_name} {i}", color, i))
        id += 1


def get_card(name):
    for card in ALL_CARDS:
        if card.name == name:
            return copy.deepcopy(card)


#################################### Non-card objects ####################################

class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def __len__(self):
        return len(self.cards)

    def __str__(self) -> str:
        return ", ".join([str(c) for c in self.cards])

    def __repr__(self) -> str:
        return ", ".join([str(c) for c in self.cards])

    def add_card(self, card):
        self.cards.append(card)

    def add_cards(self, cards):
        self.cards += cards

    def pick_card(self, card_id):
        for i, card in enumerate(self.cards):
            if card.id == card_id:
                self.cards.pop(i)
                return card

class Deck:
    def __init__(self):
        self.cards: List[Card] = []

        self.reset()

    def __len__(self):
        return len(self.cards)

    def reset(self):
        self.cards = copy.deepcopy(ALL_CARDS)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n_cards):
        drawn_cards = []
        for _ in range(n_cards):
            drawn_cards.append(self.cards.pop())
        return drawn_cards

class Trick:
    def __init__(self) -> None:
        self.cards: List[Tuple[int, Card]] = []
        self.color = None
        self.pms_played = False  # pms = pirate mermaid skullking
        self.kraken_played = False
        self.white_whale_played = False
        self.winner_id = None

    def __len__(self):
        return len(self.cards)

    def __str__(self) -> str:
        return " -> ".join([str(c) for c in self.cards])

    def __repr__(self) -> str:
        return " -> ".join([str(c) for c in self.cards])

    @property
    def bonus_points(self) -> float:
        bonus_points = 0
        for _, card in self.cards:
            bonus_points += card.bonus_points

        return bonus_points

    def add_card(self, player_id: int, card: Card):
        if len(self.cards) == 0:
            self.first_card = card

        card.trick_order = len(self.cards)

        self.cards.append((player_id, card))

        if isinstance(card, Pirate) or isinstance(card, Mermaid) or isinstance(card, SkullKing):
            self.pms_played = True
        elif isinstance(card, Kraken):
            self.kraken_played = True
        elif isinstance(card, WhiteWhale):
            self.white_whale_played = True

        # The trick gets a color if the first number played is played before a pirate, mermaid, or skull king
        if self.color is None and isinstance(card, Number) and not self.pms_played:
            self.color = card.color

    def get_first_color(self):
        return self.color

    def get_winner(self):
        """Compute the id of the player who won the trick"""
        current_winner = self.cards[0][0]
        current_winning_card = self.cards[0][1]

        # Special case: White Whale was played during the round
        if self.white_whale_played:
            highest_value = current_winning_card.value if isinstance(current_winning_card, Number) else 0
            # Only consider numbers
            for player_id, card in self.cards[1:]:
                if isinstance(card, Number):
                    if card.value > highest_value:
                        current_winning_card = card
                        current_winner = player_id

            self.winner_id = current_winner
            return current_winner

        # No white whale was played, get winner as usual

        pirate_played = isinstance(current_winning_card, Pirate)
        mermaid_played = isinstance(current_winning_card, Mermaid)
        skull_king_played = isinstance(current_winning_card, SkullKing)

        for player_id, card in self.cards[1:]:
            # Check if the current card beats the winning card
            if isinstance(card, Number):
                if card.__gt__(current_winning_card, self.color):
                    current_winner = player_id
                    current_winning_card = card
            else:
                if isinstance(card, Pirate):
                    pirate_played = True
                elif isinstance(card, Mermaid):
                    mermaid_played = True
                elif isinstance(card, SkullKing):
                    skull_king_played = True

                if card > current_winning_card:
                    current_winner = player_id
                    current_winning_card = card

        # Special case, if all three PMS are played then the mermaid wins
        if pirate_played and mermaid_played and skull_king_played:
            # Find the mermaid
            for player_id, card in self.cards:
                if isinstance(card, Mermaid):
                    current_winner = player_id
                    current_winning_card = Mermaid

        # Add bonus points if the winning card was the skull king, mermaid, or pirate
        if isinstance(current_winning_card, Pirate):
            count = 0
            for _, card in self.cards:
                if isinstance(card, Mermaid): count += 1
            current_winning_card.capture_mermaids(count)
        elif isinstance(current_winning_card, Mermaid):
            if any([isinstance(c, SkullKing) for _, c in self.cards]):
                current_winning_card.capture_skullking()
        elif isinstance(current_winning_card, SkullKing):
            count = 0
            for _, card in self.cards:
                if isinstance(card, Pirate): count += 1
            current_winning_card.capture_pirates(count)

        self.winner_id = current_winner
        return current_winner
