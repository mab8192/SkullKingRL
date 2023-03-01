import numpy as np
from agent import ManualAgent, RandomAgent, RLAgent
from game import Deck, Trick


class SkullKingGame:
    def __init__(self, n_players: int) -> None:
        super().__init__()
        self.deck = Deck()

        self.n_players = n_players
        self.round = 0
        self.current_player = 0

        # Global game state
        # - player_bets: List[int]
        # - current_trick: Trick
        # - player_scores: List[int]
        # - tricks_taken: List[int]
        # - cards_played: List[int]

        # Bet for each player in the current round.
        self.player_bets = []

        # Current trick being played
        self.current_trick = Trick()

        # Scores for each player
        self.player_scores = []

        # Number of tricks taken for each player
        self.tricks_taken = []

        # Cards played in the current round
        self.cards_played = np.zeros(len(self.deck))

        self.reset()

    def reset(self):
        self.round = 0
        self.current_player = 0
        self.player_bets = [0]*len(self.n_players)
        self.current_trick = Trick()
        self.player_scores = [0]*len(self.n_players)
        self.tricks_taken = [0]*len(self.n_players)
        self.cards_played = np.zeros(len(self.deck))

    @property
    def state(self):
        return {
            "player_bets": self.player_bets,
            "current_trick": self.current_trick,
            "player_scores": self.player_scores,
            "tricks_taken": self.tricks_taken,
            "cards_played": self.cards_played
        }

    def play_trick(self):
        """
        Starting with the current player, prompt each player to play a card for the current trick.
        """
        pass

    def play_round(self):
        """
        Starting with the current player, prompt each agent to play a card in order, updating
        the game state as we go.
        """
        # Shuffle the deck
        self.deck.reset()
        self.deck.shuffle()

        # Deal hands

        # Collect player bids
        for agent in self.agents:
            pass

        # Play each trick in the round

    def score_round(self):
        """
        Compute scores for each player for the current round.
        """
        pass

    def play_game(self):
        """
        Simulate a full game of Skull King.
        """
        pass