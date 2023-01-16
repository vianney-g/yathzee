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
class GameStarted(Event):
    pass
