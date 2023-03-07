import random
from collections import deque
from copy import deepcopy
from typing import List

import game
import numpy as np


class ReplayBuffer:
    """
    Captures interactions between agents and the environment so they can be
    used to train the neural networks for RL-based agents.
    """
    def __init__(self, capacity: int) -> None:
        self.memory = deque([], maxlen=capacity)

    def push(self, x):
        self.memory.append(x)

    def sample(self, batch_size: int):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class BaseAgent:
    """Base class for agents to extend."""
    def __init__(self, id: int) -> None:
        # Per game properties
        self.id = id

        # Per round properties
        self.bet = -1  # Bet for the current round
        self.starting_hand = game.Hand()
        self.hand = game.Hand()  # Current hand of cards
        self.tricks: List[game.Trick] = []  # List of collected tricks so far

    def compute_score(self, round_number: int) -> int:
        score = 0

        # Special case: bet 0
        if self.bet == 0:
            if len(self.tricks) == 0:
                score += round_number*10
            else:
                score -= round_number*10
        else:
            if len(self.tricks) == self.bet:
                score += 20*self.bet  # Score 20 points per trick won
                # Add bonus points, if any
                for trick in self.tricks:
                    score += trick.bonus_points
            else:
                diff = abs(self.bet - len(self.tricks))
                score -= diff*10  # Lose 10 points per trick off from `bet`
        return score

    def assign_hand(self, hand: game.Hand):
        self.starting_hand = deepcopy(hand)  # Maintain a separate copy of the starting hand.
        self.hand = hand

    def win_trick(self, trick: game.Trick):
        self.tricks.append(trick)

    def cleanup(self):
        """Cleanup intermediates between rounds"""
        self.hand = game.Hand()
        self.tricks = []
        self.bet = -1

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
        for card in self.hand.cards:
            if not isinstance(card, game.Number):
                legal_actions[card.id] = 1
            else:
                if first_color is None or card.color == first_color:
                    legal_actions[card.id] = 1
                else:
                    legal_actions[card.id] = 0

        if legal_actions.sum() == 0:
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


class RandomAgent(BaseAgent):
    """An agent that learns with delayed rewards."""
    def bid(self, game_state) -> int:
        """Make a bid prediction based on the current player's hand."""
        self.bet = random.randint(0, len(self.hand))
        return self.bet

    def play(self, game_state) -> game.Card:
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        legal_actions = self._get_legal_actions(game_state)
        choices = np.nonzero(legal_actions)[0]
        action = np.random.choice(choices)
        card = self.hand.pick_card(action)
        return card


class ManualAgent(BaseAgent):
    """An agent controlled by the command line"""
    def bid(self, game_state) -> int:
        print("\nTime to bet!")
        print("Your hand is:", self.hand)
        self.bet = int(input("Enter your bet: "))
        return self.bet

    def play(self, game_state) -> game.Card:
        print("\nYour turn to play a card!")
        print("Cards played:", game_state["current_trick"])
        print("Player bets:", game_state["player_bets"])
        print("Your hand:", self.hand)
        legal_actions = self._get_legal_actions(game_state)
        while True:
            action = int(input("Enter the card you want to play: "))
            if legal_actions[action] == 1:
                card = self.hand.pick_card(action)
                return card


class RLAgent(BaseAgent):
    """An agent that learns with delayed, sparse rewards."""
    def __init__(self, id: int, bid_replay_buffer: ReplayBuffer, play_replay_buffer: ReplayBuffer) -> None:
        super().__init__(id)

        # Extra properties for RL
        self.last_action = -1
        self.last_state = None

        # Neural Networks
        self.bid_network = None  # Network that bids on the current round, trained with supervised learning

        self.play_network = None  # Network that decides which card to play, trained with Deep Q-Learning
        self.target_network = None

        # Global memory shared by all agents
        # Reduces the number of games required to play to update the networks
        # All RL agents learn from shared experiences
        self.bid_memory = bid_replay_buffer
        self.play_memory = play_replay_buffer

    def cleanup(self):
        super().cleanup()
        self.last_action = -1
        self.last_state = None

    def bid(self):
        """Make a bid prediction based on the current player's hand."""
        raise NotImplementedError

    def play(self, state):
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        raise NotImplementedError

    def reward(self, reward):
        """Give the agent a reward for the actions played during the current round. Add experiences to memory"""
        self.bid_memory.push((self.starting_hand, len(self.tricks)))
        self.play_memory.push((self.last_state, self.last_action, reward))

    def optimize(self):
        raise NotImplementedError
