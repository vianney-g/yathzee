from abc import ABC
from dataclasses import dataclass
from typing import Literal
from uuid import UUID


class Command(ABC):
    """Send a command to yahtzee game"""


@dataclass(frozen=True)
class CreateGame(Command):
    pass


@dataclass(frozen=True)
class GameCommand(Command):
    game: UUID


@dataclass(frozen=True)
class AddPlayer(GameCommand):
    name: str


@dataclass(frozen=True)
class StartGame(GameCommand):
    pass


@dataclass(frozen=True)
class PlayerCommand(GameCommand):
    player: str


@dataclass(frozen=True)
class EndGame(GameCommand):
    pass


@dataclass(frozen=True)
class RollDices(PlayerCommand):
    pass


@dataclass(frozen=True)
class Score(PlayerCommand):
    combination: str


@dataclass(frozen=True)
class KeepDice(PlayerCommand):
    dice: Literal[1, 2, 3, 4, 5]
