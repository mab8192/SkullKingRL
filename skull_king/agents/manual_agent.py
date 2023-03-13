import logging

import skull_king.game as game
from skull_king.agents import BaseAgent


class ManualAgent(BaseAgent):
    """An agent controlled by the command line"""
    def bid(self, game_state) -> int:
        logging.info("Time to bet!")
        logging.info(f"Your hand: {self.hand}")
        self.bet = int(input("Enter your bet: "))
        return self.bet

    def play(self, game_state) -> game.Card:
        logging.info("Your turn to play a card!")
        logging.info(f"Cards played: {game_state['current_trick']}")
        logging.info(f"Player bets: {game_state['player_bets']}")
        logging.info(f"Your hand: {self.hand}")
        legal_actions = self._get_legal_actions(game_state)
        while True:
            action = int(input("Enter the card you want to play: "))
            if legal_actions[action] == 1:
                card = self.hand.pick_card(action)
                return card
