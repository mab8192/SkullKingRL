import random

import numpy as np

import skull_king.game as game
from skull_king.agents import BaseAgent


class RandomAgent(BaseAgent):
    """An agent that learns with delayed rewards."""
    def bid(self, game_state: dict) -> int:
        """Make a bid prediction based on the current player's hand."""
        self.bet = random.randint(0, len(self.hand))
        return self.bet

    def play(self, game_state: dict) -> game.Card:
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        legal_actions = self._get_legal_actions(game_state)
        choices = np.nonzero(legal_actions)[0]
        action = np.random.choice(choices)
        card = self.hand.pick_card(action)
        return card
