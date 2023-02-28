from abc import ABC
from dataclasses import dataclass
from typing import Literal
from uuid import UUID


class Event(ABC):
    ...


@dataclass
class GameCreated(Event):
    uuid: UUID


@dataclass
class PlayerAdded(Event):
    player: str


@dataclass
class GameStarted(Event):
    pass


@dataclass
class PointsScored(Event):
    player: str
    category: str
    points: int


@dataclass
class TurnChanged(Event):
    new_player: str
    round_number: int


@dataclass
class DicePositionChanged(Event):
    number: Literal[1, 2, 3, 4, 5]
    position: Literal["on_the_track", "in_the_cup", "aside"]
    value: Literal[1, 2, 3, 4, 5, 6]
