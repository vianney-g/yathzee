from typing import Literal
from uuid import UUID

from .game import Game
from .game.dices import DiceNumber
from .repository import EventsStore


class GameViews:
    def __init__(self, game_uuid: UUID, repository: EventsStore):
        self._game = Game.from_events(game_uuid, repository.get_game_events(game_uuid))
        self.logs = repository.get_events(game_uuid)

    def player(self, player_name: str) -> dict:
        for player in self._game.board.players:
            if player.name == player_name:
                return player.asdict()
        return {}

    @property
    def current_player(self) -> dict:
        round = self._game.board.round
        current_turn = round.player_turn
        if current_turn is None:
            return {}
        return current_turn.player.asdict()

    @property
    def players(self) -> list[dict]:
        return [p.asdict() for p in self._game.board.players]

    @property
    def dices(self) -> list[dict]:
        return [d.asdict() for d in self._game.board.dices.all]

    def dice(self, dice_number: Literal[1, 2, 3, 4, 5]) -> dict:
        return self._game.board.dices.get(DiceNumber(dice_number)).asdict()
