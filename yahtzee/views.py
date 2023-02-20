from .game.game import Game


class GameViews:
    def __init__(self, game: Game):
        self._game = game

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
