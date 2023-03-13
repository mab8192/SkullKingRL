import torch
import torch.nn as nn
import torch.nn.functional as F

from skull_king.agents.rl_agent import ReplayMemory, BidNetwork, PlayNetwork
from skull_king.env import SkullKingGame

def train(args):
    game = SkullKingGame(0, 0, args.n_agents)
    bid_memory = ReplayMemory()
    play_memory = ReplayMemory()

    bid_network = BidNetwork()
    play_network = PlayNetwork()
    target_network = PlayNetwork()
    target_network.load_state_dict(play_network.state_dict())
    optimizer = torch.optim.AdamW(play_network.parameters(), lr=args.lr, amsgrad=True)

    steps_done = 0
    episode_rewards = []


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-n", "--n-agents", type=int, default=4)

    args = parser.parse_args()

    train(args)
