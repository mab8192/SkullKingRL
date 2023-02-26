import random
from .cards import *

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
        self.cards = []

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
            


class Player:
    def __init__(self, id: int) -> None:
        self.id = id
        self.score = 0
        self.bet = -1
        self.hand = Hand()
        self.tricks = []

    def set_bet(self, bet: int):
        self.bet = bet

    def win_trick(self, trick: Trick):
        pass

    def compute_score(self, round_number: int):
        if self.bet == 0:
            if len(self.tricks) == 0:
                self.score += round_number*10
            else:
                self.score -= round_number*10
        else:
            pass
