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

    def __gt__(self, other):
        if not isinstance(other, Card): raise ValueError

class Number(Card):
    def __init__(self, id, name, color, value):
        super().__init__(id, name)
        self.color = color
        self.value = value

        # Assign bonus points for 14 cards
        if value == 14:
            self.bonus_points = 20 if color == "black" else 10

    def __gt__(self, other, trump_color):
        super().__gt__(other)

        if isinstance(other, Number):
            if self.color == "black" and other.color != "black":
                return True
            elif self.color != "black" and other.color == "black":
                return False
            elif self.color == trump_color and other.color != trump_color:
                return True
            elif self.color != trump_color and other.color == trump_color:
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
    def capture_mermaid(self, count):
        self.bonus_points += count*20

    def __gt__(self, other):
        super().__gt__(other)

        if isinstance(other, Number):
            return True
        elif isinstance(other, Pirate):
            return self.trick_order < other.trick_order
        elif isinstance(other, Mermaid):
            return True
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
    def capture_skullking(self):
        self.bonus_points = 50

    def __gt__(self, other):
        super().__gt__(other)

        if isinstance(other, Number):
            return True
        elif isinstance(other, Pirate):
            return False
        elif isinstance(other, Mermaid):
            return self.trick_order < other.trick_order
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
                return False
            else:
                return True
        else:
            raise NotImplementedError

class SkullKing(Card):
    def capture_pirate(self, count):
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
            return False
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
    def enable(self):
        self.bonus_points += 20

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
            return False
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

    def use_as_pirate(self, as_pirate):
        self.as_pirate = as_pirate

#################################### Non-card objects ####################################

class Hand:
    def __init__(self):
        self.cards = []

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
        self.cards = []

        self.reset()

    def __len__(self):
        return len(self.cards)

    def reset(self):
        self.cards = [
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

        id = len(self.cards)
        for color in ["black", "yellow", "green", "purple"]:
            for i in range(1, 15):
                self.cards.append(Number(id, f"{color} {i}", color, i))
                id += 1

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

    @property
    def bonus_points(self) -> float:
        bonus_points = 0
        for card in self.cards:
            bonus_points += card.bonus_points

        return bonus_points

    def add_card(self, player_id: int, card: Card):
        self.cards.append((player_id, card))

    def get_winner(self):
        """Compute the id of the player who won the trick"""
        current_winner = 0
        current_winning_card = None
        trump_color = ""

        for player_id, card in self.cards:
            pass
