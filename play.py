import logging
from skull_king.env import SkullKingGame

def main(args):
    if args.debug:
        level=logging.DEBUG
    else:
        level=logging.INFO

    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)

    n_irl = args.num_irl
    n_manual = 0
    n_random = args.num_random
    n_agents = 3 - args.num_random

    if args.mode == "singleplayer":
        n_manual = 1

    if n_manual + n_random + n_agents != 4 and n_agents > 0:
        logging.error("Must have 4 players when using a RLAgent. Try adding more random agents with --num_random <n>")

    game = SkullKingGame(n_manual=n_manual, n_random=n_random, n_irl=n_irl,
                         n_rl=n_agents, checkpoint_filepath=args.filepath)
    game.play_game()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--mode", "-m", default="singleplayer")
    parser.add_argument("--debug", "-d", action='store_true')
    parser.add_argument("-f", "--filepath", type=str, default=None)
    parser.add_argument("--num_random", type=int, default=0)
    parser.add_argument("--num_irl", type=int, default=0)

    args = parser.parse_args()
    main(args)
