import random
from collections import deque

import torch
import torch.nn as nn
import torch.nn.functional as F

from skull_king.agents import BaseAgent


class ReplayMemory:
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


class BidNetwork(nn.Module):
    def __init__(self, n_obs: int) -> None:
        super().__init__()

        self.main = nn.Sequential(
            nn.Linear(n_obs, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        return self.main(x)


class PlayNetwork(nn.Module):
    def __init__(self, n_obs: int, n_actions: int) -> None:
        super().__init__()

        self.main = nn.Sequential(
            nn.Linear(n_obs, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, n_actions)
        )

    def forward(self, x):
        return self.main(x)


class RLAgent(BaseAgent):
    """An agent that learns with delayed, sparse rewards."""
    def __init__(self,
                 id: int,
                 bid_network: torch.nn.Module,
                 play_network: torch.nn.Module,
                 target_network: torch.nn.Module) -> None:
        super().__init__(id)

        # Extra properties for RL
        self.last_action = -1
        self.last_state = None

        # Neural Networks
        self.bid_network = bid_network  # Network that bids on the current round, trained with supervised learning

        self.play_network = play_network  # Network that decides which card to play, trained with Deep Q-Learning
        self.target_network = target_network

    def cleanup(self):
        super().cleanup()
        self.last_action = -1
        self.last_state = None

    def get_obs(self, game_state) -> int:
        """
        Convert a global game_state from the environment to an observation including internal state.
        """
        pass

    @torch.no_grad()
    def bid(self):
        """Make a bid prediction based on the current player's hand."""
        raise NotImplementedError

    @torch.no_grad()
    def play(self, state):
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        raise NotImplementedError

    def optimize(self):
        raise NotImplementedError
