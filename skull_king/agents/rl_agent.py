import math
import random
from collections import deque

import numpy as np
import torch
import torch.nn as nn

from skull_king.agents import BaseAgent
from skull_king import game

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
            nn.Linear(128, 11),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.main(x)


class PlayNetwork(nn.Module):
    def __init__(self, n_obs: int, n_actions: int) -> None:
        super().__init__()

        self.main = nn.Sequential(
            nn.Linear(n_obs, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, n_actions)
        )

    def forward(self, x):
        return self.main(x)


class RLAgent(BaseAgent):
    """An agent that learns with delayed, sparse rewards."""
    def __init__(self,
                 id: int,
                 bid_network: torch.nn.Module = None,
                 play_network: torch.nn.Module = None,
                 target_network: torch.nn.Module = None,
                 play_memory: ReplayMemory = None,
                 bid_memory: ReplayMemory = None,
                 memory_size: int = 10000,
                 batch_size: int = 128,
                 gamma: float = 0.95,
                 eps_start: float = 0.95,
                 eps_end: float = 0.1,
                 eps_decay: float = 2000,
                 target_update: int = 2) -> None:
        super().__init__(id)

        # Neural Networks
        n_obs = self._get_obs_size()
        n_play_actions = len(game.ALL_CARDS)  # Total number of possible cards

        if bid_network is None:
            bid_network = BidNetwork(n_obs)
        if play_network is None:
            play_network = PlayNetwork(n_obs, n_play_actions)
        if target_network is None:
            target_network = PlayNetwork(n_obs, n_play_actions)
            target_network.load_state_dict(play_network.state_dict())

        self.bid_network = bid_network
        self.play_network = play_network
        self.target_network = target_network

        self.play_optimizer = torch.optim.Adam(self.play_network.parameters(), lr=0.00001)
        self.bid_optimizer = torch.optim.Adam(self.bid_network.parameters())

        # RL Components
        if bid_memory is None:
            self.bid_memory = ReplayMemory(memory_size)
        else:
            self.bid_memory = bid_memory

        if play_memory is None:
            self.memory = ReplayMemory(memory_size)
        else:
            self.memory = play_memory

        self.batch_size = batch_size
        self.gamma = gamma
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_decay = eps_decay
        self.target_update = target_update

        # Training State
        self.games_played = 0
        self.round_traj = [] # [(state, action, immediate_reward), ...]
        self.current_round_rewards = []
        self.current_bid: int = None

    def _get_obs_size(self, n_players: int = 4) -> int:
        cards_played_space = len(game.ALL_CARDS) # cards played in current round
        hand_space = len(game.ALL_CARDS) # cards in our hand
        trick_space = len(game.ALL_CARDS) # cards played in current trick

        is_starting_player_space = 1

        # per-player state
        bid_space = 11 # [0-10]
        score_space = 1 # raw score value
        tricks_taken_space = 10 # [0-9] (can't take the 10th unless the game is over, in which case it doesn't matter)

        player_id_space = 4 # num players
        return cards_played_space + hand_space + trick_space + is_starting_player_space \
            + n_players * (bid_space + score_space + tricks_taken_space) \
            + player_id_space

    def save(self, filepath: str) -> None:
        torch.save({
            'bid_network': self.bid_network.state_dict(),
            'play_network': self.play_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'play_optimizer': self.play_optimizer.state_dict(),
            'bid_optimizer': self.bid_optimizer.state_dict()
        }, filepath)

    def load(self, filepath: str) -> None:
        checkpoint = torch.load(filepath)
        self.bid_network.load_state_dict(checkpoint['bid_network'])
        self.play_network.load_state_dict(checkpoint['play_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.play_optimizer.load_state_dict(checkpoint['play_optimizer'])
        self.bid_optimizer.load_state_dict(checkpoint['bid_optimizer'])

    def round_cleanup(self):
        super().round_cleanup()
        self.round_traj = []
        self.current_round_rewards = []
        self.current_bid = None

    def lose_trick(self) -> None:
        pass

    def win_trick(self, trick: game.Trick) -> None:
        super().win_trick(trick)
        # base reward for winning a trick
        # negative reward if we've received too many tricks
        if self.current_bid == 0:
            reward = -10
        elif len(self.tricks) > self.current_bid:
            reward = -2
        else:
            reward = 2

        # only get extra reward if we're working towards our bid
        if (reward > 0): reward += trick.bonus_points

        # Update this tricks state-action pair with a new reward to save in memory at round end
        if self.round_traj:
            s, a, _ = self.round_traj[-1]
            self.round_traj[-1] = (s, a, reward)

    def compute_score(self, round_number, bet) -> int:
        score = super().compute_score(round_number, bet)

        # Store round info in replay memory
        final_reward = score / len(self.round_traj) / 10

        for i in range(len(self.round_traj)):
            state, action, reward = self.round_traj[i]
            total_reward = reward + final_reward
            next_state = self.round_traj[i + 1][0] if i < len(self.round_traj) -1 else None
            self.memory.push((state, action, next_state, total_reward))

        starting_state = self.round_traj[0][0]
        self.bid_memory.push((starting_state, len(self.tricks)))

        return score

    def get_epsilon(self) -> float:
        """Calculate current epsilon value for epsilon-greedy policy."""
        eps_threshold = max(self.eps_end + (self.eps_start - self.eps_end) * math.exp(-1. * self.games_played / self.eps_decay), self.eps_end)
        return eps_threshold

    def get_obs(self, game_state: dict) -> torch.Tensor:
        """
        Convert a global game_state from the environment to an observation including internal state.
        """
        obs_parts = []

        # 1. Encode cards in hand (one-hot)
        hand_encoding = torch.zeros(len(game.ALL_CARDS))
        for card in self.hand.cards:
            hand_encoding[card.id] = 1
        obs_parts.append(hand_encoding)

        # 2. Encode cards played in round (one-hot)
        round_cards_encoding = torch.zeros(len(game.ALL_CARDS))
        cards_played = game_state['cards_played']
        round_cards_encoding[cards_played == 1] = 1
        obs_parts.append(round_cards_encoding)

        # 3. Encode cards played in current trick (one-hot)
        trick_encoding = torch.zeros(len(game.ALL_CARDS))
        current_trick = game_state['current_trick']
        for _, card in current_trick.cards:
            trick_encoding[card.id] = 1
        obs_parts.append(trick_encoding)

        # 4. Encode starting player flag
        if game_state["starting_player"] == self.id:
            obs_parts.append(torch.Tensor([1.0]))
        else:
            obs_parts.append(torch.Tensor([0.0]))

        # 5. Encode player states
        for i in range(4):  # For each possible player
            # Encode bid (one-hot)
            bid_encoding = torch.zeros(11)
            if i < len(game_state['player_bets']):
                bid = int(game_state['player_bets'][i])
                if 0 <= bid <= 10:
                    bid_encoding[bid] = 1
            obs_parts.append(bid_encoding)

            # Raw score (continuous value)
            if i < len(game_state['player_scores']):
                score = torch.tensor([game_state['player_scores'][i]], dtype=torch.float32)
            else:
                score = torch.tensor([0.0])
            obs_parts.append(score)

            # Encode tricks taken (one-hot)
            tricks_encoding = torch.zeros(10)
            if i < len(game_state['tricks_taken']):
                tricks = int(game_state['tricks_taken'][i])
                if 0 <= tricks <= 9:
                    tricks_encoding[tricks] = 1
            obs_parts.append(tricks_encoding)

        # 6. Encode player id
        id_encoding = torch.zeros(4)
        id_encoding[self.id] = 1
        obs_parts.append(id_encoding)

        return torch.cat(obs_parts)

    @torch.no_grad()
    def bid(self, game_state: dict) -> int:
        """Make a bid prediction based on the current player's hand."""
        obs = self.get_obs(game_state)
        bid_logits = self.bid_network(obs.unsqueeze(0))
        bid_mask = torch.cat((torch.ones(game_state["current_round"] + 1), torch.zeros(10 - game_state["current_round"])))
        masked_logits = bid_logits.masked_fill(bid_mask == 0, float('-inf'))
        self.current_bid = masked_logits.argmax().item()
        return self.current_bid

    @torch.no_grad()
    def play(self, game_state: dict) -> int:
        """Play a card from the agent's hand, given the current global state and the agent's internal state."""
        obs = self.get_obs(game_state)
        self.last_obs = obs

        # Get legal actions using base class method
        legal_actions = torch.tensor(
            self._get_legal_actions(game_state),
            dtype=torch.float32
        )

        # Epsilon-greedy action selection
        if random.random() > self.get_epsilon():
            # Get action probabilities and mask invalid actions
            logits: torch.Tensor = self.play_network(obs.unsqueeze(0))

            masked_logits = logits.masked_fill(legal_actions == 0, float('-inf'))
            action_probs = torch.softmax(masked_logits, dim=-1)

            if (action_probs.sum() > 0):
                action_probs /= action_probs.sum()
            else:
                print(f"Current hand: {self.hand}")
                print(f"Legal actions {legal_actions}")
                print(f"logits: {logits}")
                print(f"action_probs: {action_probs}")
                raise ValueError("Invalid card chosen! See logs above for more information.")

            action_id = torch.multinomial(action_probs, 1).item()
        else:
            # Random choice from legal actions
            choices = torch.nonzero(legal_actions).flatten()
            action_id = choices[torch.randint(0, len(choices), (1,))].item()

        self.round_traj.append((obs, action_id, 0))  # Initial reward is 0

        # Find and return the matching card from hand
        card = self.hand.pick_card(action_id)
        if card is not None:
            return card

        raise ValueError(f"Selected card ID {action_id} not found in hand! Current hand: {self.hand}")

    def optimize(self, batch_size: int = None):
        """Perform one step of optimization on the Q-network."""
        if batch_size is None:
            batch_size = self.batch_size

        if len(self.memory) < batch_size or len(self.bid_memory) < batch_size:
            return

        self.games_played += 1

        transitions = self.memory.sample(batch_size)
        batch = list(zip(*transitions))

        state_batch = torch.stack([s.float() for s in batch[0]])
        action_batch = torch.tensor([a for a in batch[1]], dtype=torch.long)
        next_state_batch = torch.stack([s.float() for s in batch[2] if s is not None])
        reward_batch = torch.tensor([r for r in batch[3]], dtype=torch.float32)

        # Compute Q(s_t, a)
        state_action_values = self.play_network(state_batch).gather(1, action_batch.unsqueeze(1))

        # Compute V(s_{t+1}) for all next states
        next_state_values = torch.zeros(batch_size)
        non_terminal_mask = torch.tensor([s is not None for s in batch[2]], dtype=torch.bool)
        if len(next_state_batch) > 0:
            next_state_values[non_terminal_mask] = self.target_network(next_state_batch).max(1)[0]

        # Compute the expected Q values
        expected_state_action_values = (next_state_values * self.gamma) + reward_batch

        # Compute loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the play network
        self.play_optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_norm_(self.play_network.parameters(), max_norm=1.0)
        self.play_optimizer.step()

        # Update target network
        if self.games_played % self.target_update == 0:
            self.target_network.load_state_dict(self.play_network.state_dict())

        # Optimize bid network
        bid_transitions = self.bid_memory.sample(batch_size)
        bid_batch = list(zip(*bid_transitions))

        bid_state_batch = torch.stack([s for s in bid_batch[0]])
        bid_target_batch = torch.tensor([t for t in bid_batch[1]], dtype=torch.long)

        # Compute loss for bid network
        try:
            bid_output = self.bid_network(bid_state_batch)
            bid_loss = nn.CrossEntropyLoss()(bid_output, bid_target_batch)
        except Exception as e:
            print(str(e))
            print(bid_state_batch)
            print(bid_target_batch)

        # Optimize the bid network
        self.bid_optimizer.zero_grad()
        bid_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.bid_network.parameters(), max_norm=1.0)
        self.bid_optimizer.step()

        if self.id == 3:
            # with torch.no_grad():
            #     print(f"[Agent {self.id}] Debug info:")
            #     print(f"  Reward range: [{reward_batch.min():.2f}, {reward_batch.max():.2f}]")
            #     print(f"  Q-value range: [{state_action_values.min():.2f}, {state_action_values.max():.2f}]")
            #     print(f"  Target range: [{expected_state_action_values.min():.2f}, {expected_state_action_values.max():.2f}]")
            print(f"  Losses: play loss = {loss}\tbid loss = {bid_loss}\t eps = {self.get_epsilon():.4f}")
