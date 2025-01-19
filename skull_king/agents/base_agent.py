from copy import deepcopy
from typing import List

import numpy as np

import skull_king.game as game


class BaseAgent:
    """Base class for agents to extend."""
    def __init__(self, id: int) -> None:
        # Per game properties
        self.id = id

        # Per round properties
        self.starting_hand = game.Hand()
        self.hand = game.Hand()  # Current hand of cards
        self.tricks: List[game.Trick] = []  # List of collected tricks so far

    def compute_score(self, round_number: int, bet: int) -> int:
        score = 0

        # Special case: bet 0
        if bet == 0:
            if len(self.tricks) == 0:
                score += round_number*10
            else:
                score -= round_number*10
        else:
            if len(self.tricks) == bet:
                score += 20*bet  # Score 20 points per trick won
                # Add bonus points, if any
                for trick in self.tricks:
                    score += trick.bonus_points
            else:
                diff = abs(bet - len(self.tricks))
                score -= diff*10  # Lose 10 points per trick off from `bet`
        return score

    def assign_hand(self, hand: game.Hand):
        self.starting_hand = deepcopy(hand)  # Maintain a separate copy of the starting hand.
        self.hand = hand

    def lose_trick(self) -> None:
        # No-op for base agent
        pass

    def win_trick(self, trick: game.Trick) -> None:
        self.tricks.append(trick)

    def round_cleanup(self):
        """Cleanup intermediates between rounds"""
        self.starting_hand = game.Hand()
        self.hand = game.Hand()
        self.tricks = []

    def _get_legal_actions(self, game_state: dict) -> np.ndarray:
        """
        Of the cards in this agent's hand, return only those which are legal to play.
        game_state will contain the following information:
            - player_bets: List[int]
            - current_trick: Trick
            - player_scores: List[int]
            - tricks_taken: List[int]
            - cards_played: List[int]
        """
        legal_actions = np.zeros(len(game.ALL_CARDS))

        current_trick: game.Trick = game_state["current_trick"]
        if len(current_trick) == 0:
            # No cards in current trick, all cards can be played
            legal_actions[[card.id for card in self.hand.cards]] = 1
            return legal_actions

        # At least one card has been played
        first_color = current_trick.get_first_color()
        first_color_cards = 0  # Track the number of cards you have of the first color played
        for card in self.hand.cards:
            if not isinstance(card, game.Number):
                legal_actions[card.id] = 1
            else:
                if first_color is None or card.color == first_color:
                    legal_actions[card.id] = 1
                    first_color_cards += 1
                else:
                    legal_actions[card.id] = 0

        if first_color_cards == 0:
            # We don't have any cards that match the first color, we can play any card
            for card in self.hand.cards:
                legal_actions[card.id] = 1

        return legal_actions

    def bid(self, game_state) -> int:
        """Make a bid prediction based on the current player's hand and the global game state."""
        raise NotImplementedError

    def play(self, game_state) -> game.Card:
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        raise NotImplementedError
