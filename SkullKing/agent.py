import random
from collections import deque
from typing import List
from copy import deepcopy

from game import Hand, Trick


class MemoryReplay:
    def __init__(self, capacity: int) -> None:
        self.memory = deque([], maxlen=capacity)

    def push(self, x):
        self.memory.append(x)

    def sample(self, batch_size: int):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class Agent:
    """An agent that learns with delayed rewards."""
    def __init__(self, id: int, memory_capacity: int = 10_000) -> None:
        # Per game properties
        self.id = id
        self.score = 0

        # Per round properties
        self.bet = -1  # Bet for the current round
        self.starting_hand = Hand()
        self.hand = Hand()  # Current hand of cards
        self.tricks: List[Trick] = []  # List of collected tricks so far
        self.last_action = -1
        self.last_state = None

        # DQNs
        self.bid_network = None  # Network that bids on the current round
        self.play_network = None  # Network that decides which card to play

        self.bid_memory = MemoryReplay(memory_capacity)
        self.play_memory = MemoryReplay(memory_capacity)

        # TODO: future properties
        self.loot_with = -1  # Flag to indicate if a player has loot with anyone
        self.wager = 0  # Ability to wager with Rascal of Roatan

    def compute_score_for_round(self, round_number: int):
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

    def assign_hand(self, hand: Hand):
        self.starting_hand = deepcopy(hand)  # Maintain a separate copy of the starting hand.
        self.hand = hand

    def cleanup(self):
        """Cleanup intermediates between rounds"""
        self.hand = Hand()
        self.tricks = []
        self.bet = -1

    def bid(self):
        """Make a bid prediction based on the current player's hand."""
        self.bet = 0

    def _get_legal_actions(self, state):
        """Of the cards in this agent's hand, return only those which are legal to play."""
        pass

    def play(self, state):
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        self.last_state = state

    def reward(self, reward):
        """Give the agent a reward for the actions played during the current round. Add experiences to memory"""
        self.bid_memory.push((self.starting_hand, self.bet, len(self.tricks)))
        self.play_memory.push((self.last_state, self.last_action, reward))

    def optimize(self):
        pass
