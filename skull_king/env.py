import logging
from typing import List
import numpy as np
from skull_king.agents import ManualAgent, RandomAgent, RLAgent, BaseAgent
from skull_king.agents.rl_agent import ReplayMemory
from skull_king.game import Deck, Trick, Hand, Loot


class SkullKingGame:
    def __init__(self, n_manual: int = 1, n_random: int = 3, n_irl: int = 0, n_rl: int = 0, checkpoint_filepath: str = None) -> None:
        super().__init__()
        self.deck = Deck()
        self.deck.reset()
        self.deck.shuffle()

        self.n_players = n_manual + n_random + n_rl
        self.round = 0
        self.starting_player = np.random.randint(0, self.n_players)  # Start with a random player

        # Init agents
        self.players: List[BaseAgent] = []
        pid = 0
        for _ in range(n_manual):
            self.players.append(ManualAgent(pid))
            pid += 1

        for _ in range(n_random):
            self.players.append(RandomAgent(pid))
            pid += 1

        # TODO: Add IRL support

        # Shared memory
        play_memory = ReplayMemory(100000)
        bid_memory = ReplayMemory(100000)
        for _ in range(n_rl):
            agent = RLAgent(pid, play_memory=play_memory, bid_memory=bid_memory)
            if (checkpoint_filepath is not None):
                agent.load(checkpoint_filepath)
            self.players.append(agent)
            pid += 1

        # History tracking
        # [[player bids, tricks taken], [player bids, tricks taken]]
        # e.g. [[[0, 0, 1, 0], [0, 0, 1, 0]], [[1, 1, 0, 0], [1, 0, 1, 0]], ...]
        self.bid_states = []

        # [round1, round2, round3, ...]
        # rounds look like [trick1, trick2, trick3, ...]
        # tricks look like [(state, action, reward), (state, action, reward), ...]
        #   where state includes global game state and the player's internal state
        # Overall structure looks like (2 player game example):
        # - [[[(state, action, reward), (state, action, reward)]], [[(state, action, reward), (state, action, reward)],[(state, action, reward), (state, action, reward)]]]
        self.action_states = []

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

        self.loot13 = [-1, -1]  # Tracks which players are connected with loot id 13
        self.loot14 = [-1, -1]  # Tracks which players are connected with loot id 14

    def reset_game(self):
        """
            Resets the game to play again from scratch
        """
        self.deck.reset()
        self.deck.shuffle()
        self.round = 0
        self.done = False
        self.starting_player = np.random.randint(0, self.n_players)  # Start with a random player
        self.player_bets = np.zeros(self.n_players)
        self.current_trick = Trick()
        self.player_scores = np.zeros(self.n_players)
        self.tricks_taken = np.zeros(self.n_players)
        self.cards_played = np.zeros(len(self.deck))
        self.loot13 = [-1, -1]
        self.loot14 = [-1, -1]

    @property
    def state(self):
        return {
            "current_round": self.round,
            "player_bets": self.player_bets,
            "current_trick": self.current_trick,
            "player_scores": self.player_scores,
            "tricks_taken": self.tricks_taken,
            "cards_played": self.cards_played,
            "starting_player": self.starting_player
        }

    def play_trick(self):
        """
        Starting with the starting player, prompt each player to play a card for the current trick.
        """
        i = self.starting_player
        while True:
            cur_player: BaseAgent = self.players[i]
            self.current_trick.add_card(i, cur_player.play(self.state))

            i = (i + 1) % self.n_players
            if i == self.starting_player: break

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

        logging.info(f"Player {self.starting_player} will start the round.")

        # Collect player bids
        for i, player in enumerate(self.players):
            self.player_bets[i] = player.bid(self.state)

        # Play each trick in the round
        for _ in range(self.round):
            self.play_trick()
            logging.info(f"Final trick state: {self.current_trick}")

            winner_id = self.current_trick.get_winner()

            if not self.current_trick.kraken_played:
                logging.info(f"Player {winner_id} won the trick.")
                for i, player in enumerate(self.players):
                    if i == winner_id: player.win_trick(self.current_trick)
                    else: player.lose_trick()
                self.tricks_taken[winner_id] += 1  # current_player is now the winner of the current trick
            else:
                logging.info(f"Kraken played! No one wins the trick. Player {winner_id} will start next.")
                # Everyone loses the trick when the kraken gets played
                for i, player in enumerate(self.players):
                    player.lose_trick()

            # Check for loot and update assignments for the round
            for player_id, card in self.current_trick.cards:
                if isinstance(card, Loot):
                    if card.id == 13:
                        self.loot13[0] = player_id
                        self.loot13[1] = self.starting_player
                    elif card.id == 14:
                        self.loot14[0] = player_id
                        self.loot14[1] = self.starting_player

            # Reset trick
            self.current_trick = Trick()

            # Winner starts the next trick
            self.starting_player = winner_id

    def score_loot(self, loot):
        """
        Check loot and player bids for additional bonus points
        """
        bonus_points = np.zeros(self.n_players)
        p1 = loot[0]
        p2 = loot[1]
        if p1 != -1 and p1 != p2:
            # Loot is valid, check bids
            if self.tricks_taken[p1] == self.player_bets[p1] and self.tricks_taken[p2] == self.player_bets[p2]:
                # Bids are valid, add bonus points
                bonus_points[p1] += 20
                bonus_points[p2] += 20

        return bonus_points

    def score_round(self):
        """
        Compute scores for each player for the current round.
        """
        round_scores = np.zeros(self.n_players)
        for i, player in enumerate(self.players):
            round_scores[i] += player.compute_score(self.round, self.player_bets[i])

        round_scores += self.score_loot(self.loot13)
        round_scores += self.score_loot(self.loot14)

        return round_scores

    def cleanup_round(self):
        """
        Clean up any intermediates created during the last round.
        """
        for player in self.players:
            player.round_cleanup()

        # Shuffle the deck
        self.deck.reset()
        self.deck.shuffle()

        # Randomly choose a new starting player for next round
        self.starting_player = np.random.randint(0, self.n_players)

        # Reset player bets
        self.player_bets = np.zeros(self.n_players)

        # Reset current trick
        self.current_trick = Trick()

        # Reset played cards
        self.cards_played = np.zeros(len(self.deck))

        # Reset tricks taken
        self.tricks_taken = np.zeros(self.n_players)

        # Reset loot
        self.loot13 = [-1, -1]
        self.loot14 = [-1, -1]

    def play_game(self):
        """
        Simulate a full game of Skull King.
        """
        # Game plays for 10 rounds
        for i in range(1, 11):
            self.round = i
            logging.debug(f"Starting round {self.round}")
            self.play_round()
            round_scores = self.score_round()
            logging.info(f"Player bets: {self.player_bets}")
            logging.info(f"Tricks taken: {self.tricks_taken}")
            logging.info(f"Old scores: {self.player_scores}")
            self.player_scores += round_scores
            logging.info(f"\nScores are now: {self.player_scores}\n")

            self.cleanup_round()

        self.done = True
