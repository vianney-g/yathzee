import dataclasses
from collections import Counter
from itertools import cycle

from .errors import YahtzeeError


@dataclasses.dataclass
class Player:
    name: str
    score: int = 0


class Players:
    def __init__(self, players: list[Player]):
        self._assert_players_are_valid(players)
        self.players = players
        self.turn_cycle = cycle(self.players)
        self.leader = next(self.turn_cycle)

    @classmethod
    def _assert_players_are_valid(cls, players: list[Player]):
        if not players:
            raise YahtzeeError("Can't create a game with no player")
        cls._assert_no_players_with_same_name(players)

    @classmethod
    def _assert_no_players_with_same_name(cls, players: list[Player]):
        name_count = Counter(player.name for player in players)
        most_common_name, count = name_count.most_common(1)[0]
        if count > 1:
            raise YahtzeeError(f"A player named {most_common_name} already exists")


@dataclasses.dataclass
class Game:
    players: Players
