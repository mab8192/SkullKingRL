from skull_king.env import SkullKingGame
import skull_king.game as game
import random


def test_many_games():
    for _ in range(50):
        skg = SkullKingGame(0, random.randint(2, 6), 0)
        skg.play_game()


def test_trick_numbers_samecolors():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Yellow 5"))
    trick.add_card(1, game.get_card("Yellow 6"))
    trick.add_card(2, game.get_card("Yellow 7"))
    trick.add_card(3, game.get_card("Yellow 8"))
    assert trick.get_winner() == 3


def test_trick_numbers_different_colors():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Yellow 5"))
    trick.add_card(1, game.get_card("Pink 6"))
    trick.add_card(2, game.get_card("Green 7"))
    trick.add_card(3, game.get_card("Pink 8"))
    assert trick.get_winner() == 0


def test_trick_numbers_black_trumps():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Yellow 5"))
    trick.add_card(1, game.get_card("Yellow 6"))
    trick.add_card(2, game.get_card("Yellow 7"))
    trick.add_card(3, game.get_card("Black 1"))
    assert trick.get_winner() == 3


def test_all_escapes():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Escape"))
    trick.add_card(1, game.get_card("Escape"))
    trick.add_card(2, game.get_card("Escape"))
    trick.add_card(3, game.get_card("Escape"))
    assert trick.get_winner() == 0


def test_escapes_and_loot():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Escape"))
    trick.add_card(1, game.get_card("Loot"))
    trick.add_card(2, game.get_card("Loot"))
    trick.add_card(3, game.get_card("Escape"))
    assert trick.get_winner() == 0


def test_escapes_and_whitewhale():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Escape"))
    trick.add_card(1, game.get_card("Loot"))
    trick.add_card(2, game.get_card("White Whale"))
    trick.add_card(3, game.get_card("Escape"))
    assert trick.get_winner() == 0


def test_escape_loot_kraken_whitewhale():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Escape"))
    trick.add_card(1, game.get_card("Loot"))
    trick.add_card(2, game.get_card("White Whale"))
    trick.add_card(3, game.get_card("Kraken"))
    assert trick.get_winner() == 0


def test_white_whale_pms():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Black 7"))
    trick.add_card(1, game.get_card("Skull King"))
    trick.add_card(2, game.get_card("White Whale"))
    trick.add_card(3, game.get_card("Yellow 10"))
    assert trick.get_winner() == 3


def test_mermaids():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Black 10"))
    trick.add_card(1, game.get_card("Skull King"))
    trick.add_card(2, game.get_card("Escape"))
    trick.add_card(3, game.get_card("Alyra"))
    assert trick.get_winner() == 3


def test_pirates():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Black 10"))
    trick.add_card(1, game.get_card("Harry the Giant"))
    trick.add_card(2, game.get_card("Escape"))
    trick.add_card(3, game.get_card("Alyra"))
    assert trick.get_winner() == 1


def test_skullking():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Black 10"))
    trick.add_card(1, game.get_card("Harry the Giant"))
    trick.add_card(2, game.get_card("Escape"))
    trick.add_card(3, game.get_card("Skull King"))
    assert trick.get_winner() == 3


def test_pms():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Black 10"))
    trick.add_card(1, game.get_card("Harry the Giant"))
    trick.add_card(2, game.get_card("Sirena"))
    trick.add_card(3, game.get_card("Skull King"))
    assert trick.get_winner() == 2


def test_mps():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Black 10"))
    trick.add_card(1, game.get_card("Sirena"))
    trick.add_card(2, game.get_card("Harry the Giant"))
    trick.add_card(3, game.get_card("Skull King"))
    assert trick.get_winner() == 1


def test_bonus_points_numbers():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Yellow 14"))
    trick.add_card(1, game.get_card("Green 14"))
    trick.add_card(2, game.get_card("Pink 14"))
    trick.add_card(3, game.get_card("Yellow 5"))
    assert trick.get_winner() == 0
    assert trick.bonus_points == 30


def test_bonus_points_black():
    trick = game.Trick()
    trick.add_card(0, game.get_card("Yellow 5"))
    trick.add_card(1, game.get_card("Yellow 6"))
    trick.add_card(2, game.get_card("Yellow 7"))
    trick.add_card(3, game.get_card("Black 14"))
    assert trick.get_winner() == 3
    assert trick.bonus_points == 20
