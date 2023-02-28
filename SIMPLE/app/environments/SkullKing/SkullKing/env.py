import gym
from gym import spaces
import numpy as np

from .objs import Deck, Player, Trick

class SkullKingEnv(gym.Env):
    def __init__(self, n_players: int) -> None:
        super().__init__()
        self.name = "Skull King"

        self.deck = Deck()
        self.n_players = n_players

        self.round = 0
        self.current_player = 0
        self.current_trick = Trick()

        self.players = []
        player_id = 0
        for _ in range(n_players):
            self.players.append(Player(player_id))

        self.total_cards = len(self.deck)

        # Action space is the total number of cards in the deck
        # Each action corresponds to a single bet or a single card.
        # Bets can range from [0, 10] for a total of 11 possible bet actions.
        self.action_space = spaces.Discrete(11 + self.total_cards)

        # Construct the observation space
        # Consists of:
        #   your hand, which moves are legal, each player's bets, each player's scores,
        #   the cards that have been played previously, your turn in the order of play,
        #   round number, cards that have been played in the current trick''''
        self.observation_space = ... # TODO

        self.reset()

    def reset(self) -> None:
        return self.observation

    @property
    def observation(self):
        pass

    def legal_actions(self):
        """Return a mask for which moves are legal for each player"""
        pass

    def step(self, action):
        """
        A single step is a single agent playing a single card.
        When a player plays a card:
            1. Check if the round is over.
            2. If the round is not over, continue play
            3. If the round is over, determine who won the trick and prompt them to play next.
        """
        pass
