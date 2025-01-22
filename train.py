import os

from skull_king.env import SkullKingGame
from skull_king.agents import RLAgent

def train(args):
    game = SkullKingGame(n_manual=0, n_random=4 - args.n_agents, n_rl=args.n_agents)

    # Modified version of game.play_game to allow for training
    for i in range(args.num_episodes):
        for i in range(1, 11):
            game.round = i
            game.play_round()
            round_scores = game.score_round()
            game.player_scores += round_scores

            game.cleanup_round()
            for player in game.players:
                if isinstance(player, RLAgent):
                    player.optimize()

        game.reset_game()

    print("Saving networks")
    os.makedirs("local", exist_ok=True)
    for i, player in enumerate(game.players):
        if isinstance(player, RLAgent):
            player.save(f"local/player_{i}.torch")

    samples = player.memory.sample(5)
    for sample in samples:
        print("=======================================================")
        print("state:", sample[0])
        print("action:", sample[1])
        print("next state:", sample[2])
        print("reward:", sample[3])

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-n", "--n-agents", type=int, default=4)
    parser.add_argument("--num_episodes", type=int, default=100)

    args = parser.parse_args()

    train(args)
