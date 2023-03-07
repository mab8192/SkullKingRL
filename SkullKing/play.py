from env import SkullKingGame

def main(args):
    game = SkullKingGame(0, 4)
    game.reset()
    game.play_game()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--mode", "-m", default="manual")
    parser.add_argument("--n-players", "-n", type=int, default=4)

    args = parser.parse_args()
    main(args)
