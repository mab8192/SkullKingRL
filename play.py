import logging
from skull_king.env import SkullKingGame

def main(args):
    if args.debug:
        level=logging.DEBUG
    else:
        level=logging.INFO

    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)

    if args.mode == "manual":
        nm = 1
        nr = 3
    else:
        nm = 0
        nr = 4

    game = SkullKingGame(nm, nr)
    game.reset()
    game.play_game()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--mode", "-m", default="manual")
    parser.add_argument("--n-players", "-n", type=int, default=4)
    parser.add_argument("--debug", "-d", action='store_true')

    args = parser.parse_args()
    main(args)
