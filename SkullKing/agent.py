import random
from collections import deque
from typing import List
from copy import deepcopy
import numpy as np

import game


class ReplayBuffer:
    def __init__(self, capacity: int) -> None:
        self.memory = deque([], maxlen=capacity)

    def push(self, x):
        self.memory.append(x)

    def sample(self, batch_size: int):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class BaseAgent:
    """An agent that learns with delayed rewards."""
    def __init__(self, id: int) -> None:
        # Per game properties
        self.id = id
        self.score = 0

        # Per round properties
        self.bet = -1  # Bet for the current round
        self.starting_hand = game.Hand()
        self.hand = game.Hand()  # Current hand of cards
        self.tricks: List[game.Trick] = []  # List of collected tricks so far

        self.current_position = 0  # Position in play

        # TODO: future properties
        self.loot_with = -1  # Flag to indicate if a player has loot with anyone
        self.wager = 0  # Ability to wager with Rascal of Roatan

    def compute_score(self, round_number: int):
        # Special case: bet 0
        if self.bet == 0:
            if len(self.tricks) == 0:
                self.score += round_number*10
            else:
                self.score -= round_number*10
        else:
            if len(self.tricks) == self.bet:
                self.score += 20*self.bet  # Score 20 points per trick won
                # Add bonus points, if any
                for trick in self.tricks:
                    self.score += trick.bonus_points
            else:
                diff = abs(self.bet - len(self.tricks))
                self.score -= diff*10  # Lose 10 points per trick off from `bet`

    def assign_hand(self, hand: game.Hand):
        self.starting_hand = deepcopy(hand)  # Maintain a separate copy of the starting hand.
        self.hand = hand

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
        trump_color = current_trick.get_trump_color()
        for card in self.hand.cards:
            if not isinstance(card, game.Number):
                legal_actions[card.id] = 1
            else:
                if trump_color is None or card.color == trump_color:
                    legal_actions[card.id] = 1
                else:
                    legal_actions[card.id] = 0

        return legal_actions

    def bid(self):
        """Make a bid prediction based on the current player's hand."""
        raise NotImplementedError

    def play(self, game_state):
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        raise NotImplementedError


class RLAgent(BaseAgent):
    """An agent that learns with delayed rewards."""
    def __init__(self, id: int, bid_replay_buffer: ReplayBuffer, play_replay_buffer: ReplayBuffer) -> None:
        super().__init__(id)

        raise NotImplementedError

        # Extra properties for RL
        self.last_action = -1
        self.last_state = None

        # Neural Networks
        self.bid_network = None  # Network that bids on the current round, trained with supervised learning

        self.play_network = None  # Network that decides which card to play, trained with Deep Q-Learning
        self.target_network = None

        # Global memory shared by all agents
        # Reduces the number of games required to play to update the networks
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


class RandomAgent(BaseAgent):
    """An agent that learns with delayed rewards."""
    def bid(self):
        """Make a bid prediction based on the current player's hand."""
        self.bet = random.randint(0, len(self.hand))
        return self.bet

    def play(self, game_state):
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        legal_actions = self._get_legal_actions(game_state)
        choices = np.nonzero(legal_actions)
        action = np.random.choice(choices)
        return action


class ManualAgent(BaseAgent):
    """An agent controlled by the command line"""
    def bid(self):
        print(self.hand)
        self.bet = int(input("Enter your bet: "))
        return self.bet

    def play(self, game_state):
        print(game_state["current_trick"])
        print("You bet:", self.bet)
        print("Your hand:", self.hand)
        legal_actions = self._get_legal_actions(game_state)
        while True:
            action = int(input("Enter the card you want to play: "))
            if legal_actions[action] == 1:
                return action
