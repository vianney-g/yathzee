from abc import ABC
from dataclasses import dataclass
from uuid import UUID


class Event(ABC):
    """Event in the system"""


@dataclass
class GameCreated(Event):
    uuid: UUID


@dataclass
class PlayerAdded(Event):
    player_name: str


@dataclass
class ErrorRaised(Event):
    msg: str


@dataclass
class GameStarted(Event):
    pass


@dataclass
class PointsScored(Event):
    player_name: str
    category: str
    points: int


@dataclass
class TurnChanged(Event):
    new_player: str
    round_number: int
