from typing import List
import numpy as np
from agents import ManualAgent, RandomAgent, RLAgent, BaseAgent
from game import Deck, Trick, Hand


class SkullKingGame:
    def __init__(self, n_manual: int = 1, n_random: int = 3, n_rl: int = 0) -> None:
        super().__init__()
        self.deck = Deck()

        self.n_players = n_manual + n_random + n_rl
        self.round = 0
        self.current_player = np.random.randint(0, self.n_players)  # Start with a random player

        # Init agents
        self.players: List[BaseAgent] = []
        pid = 0
        for _ in range(n_manual):
            self.players.append(ManualAgent(pid))
            pid += 1

        for _ in range(n_random):
            self.players.append(RandomAgent(pid))
            pid += 1

        for _ in range(n_rl):
            self.players.append(RLAgent(pid))
            pid += 1

        # Global game state
        # - player_bets: List[int]
        # - current_trick: Trick
        # - player_scores: List[int]
        # - tricks_taken: List[int]
        # - cards_played: List[int]

        # Bet for each player in the current round.
        self.player_bets = np.zeros(self.n_players)

        # Current trick being played
        self.current_trick = Trick()

        # Scores for each player
        self.player_scores = np.zeros(self.n_players)

        # Number of tricks taken for each player
        self.tricks_taken = np.zeros(self.n_players)

        # Cards played in the current round
        self.cards_played = np.zeros(len(self.deck))

        self.reset()

    def reset(self):
        self.round = 0
        self.current_player = np.random.randint(0, self.n_players)  # Start with a random player
        self.player_bets = np.zeros(self.n_players)
        self.current_trick = Trick()
        self.player_scores = np.zeros(self.n_players)
        self.tricks_taken = np.zeros(self.n_players)
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
        i = self.current_player
        trick_order = 0
        while True:
            cur_player: BaseAgent = self.players[i]
            card = cur_player.play(self.state)
            card.trick_order = trick_order
            self.current_trick.add_card(i, card)

            trick_order += 1
            i = (i + 1) % self.n_players
            if i == self.current_player: break

    def play_round(self):
        """
        Starting with the current player, prompt each agent to play a card in order, updating
        the game state as we go.
        """
        # Deal hands
        for i, player in enumerate(self.players):
            hand = Hand()
            hand.add_cards(self.deck.draw(self.round))
            player.assign_hand(hand)

        # Collect player bids
        for i, player in enumerate(self.players):
            self.player_bets[i] = player.bid(self.state)

        # Play each trick in the round
        for _ in range(self.round):
            self.play_trick()
            print("Getting winner for trick:", self.current_trick)
            self.current_player = self.current_trick.get_winner()

            if not self.current_trick.kraken_played:
                self.players[self.current_player].win_trick(self.current_trick)
                self.tricks_taken[self.current_player] += 1  # current_player is now the winner of the current trick

            print(f"Player {self.current_player} won the trick.")

    def score_round(self):
        """
        Compute scores for each player for the current round.
        """
        for i, player in enumerate(self.players):
            self.player_scores[i] += player.compute_score(self.round)

    def cleanup_round(self):
        """
        Clean up any intermediates created during the last round.
        """
        for player in self.players:
            player.cleanup()

        # Shuffle the deck
        self.deck.reset()
        self.deck.shuffle()

        # Randomly choose a new starting player for next round
        self.current_player = np.random.randint(0, self.n_players)

        # Reset player bets
        self.player_bets = np.zeros(self.n_players)

        # Reset current trick
        self.current_trick = Trick()

        # Reset tricks taken
        self.tricks_taken = np.zeros(self.n_players)

    def play_game(self):
        """
        Simulate a full game of Skull King.
        """
        # Game plays for 10 rounds
        for i in range(1, 11):
            self.round = i
            print("\nStarting round", self.round)
            self.play_round()
            self.score_round()
            self.cleanup_round()
            print("Scores are now:", self.player_scores)
