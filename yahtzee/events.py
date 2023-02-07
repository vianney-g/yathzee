import dataclasses
from abc import ABC
from uuid import UUID


class Event(ABC):
    """Event in the system"""


@dataclasses.dataclass
class GameCreated(Event):
    uuid: UUID


@dataclasses.dataclass
class PlayerAdded(Event):
    player_name: str


@dataclasses.dataclass
class ErrorRaised(Event):
    msg: str


@dataclasses.dataclass
class GameStarted(Event):
    pass


@dataclasses.dataclass
class PointsScored(Event):
    player_name: str
    category: str
    points: int


@dataclasses.dataclass
class TurnChanged(Event):
    new_player: str
    round_number: int
