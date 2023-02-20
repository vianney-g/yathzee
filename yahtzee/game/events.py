from abc import ABC
from dataclasses import dataclass
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
