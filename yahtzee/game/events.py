from abc import ABC
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypeVar
from uuid import UUID


@dataclass(frozen=True)
class Event(ABC):
    game: UUID


@dataclass(frozen=True)
class GameCreated(Event):
    pass


@dataclass(frozen=True)
class GameStarted(Event):
    pass


@dataclass(frozen=True)
class GameEnded(Event):
    pass


@dataclass(frozen=True)
class PlayerAdded(Event):
    player: str


@dataclass(frozen=True)
class PointsScored(Event):
    player: str
    category: str
    points: int


@dataclass(frozen=True)
class TurnChanged(Event):
    new_player: str
    round_number: int


@dataclass(frozen=True)
class RollPerformed(Event):
    attempt_nb: int


@dataclass(frozen=True)
class DicePositionChanged(Event):
    number: Literal[1, 2, 3, 4, 5]
    position: Literal["on_the_track", "in_the_cup", "aside"]
    value: Literal[1, 2, 3, 4, 5, 6]


E = TypeVar("E", bound=Event)
EventHandler = Callable[[E], None]


class _EventBus:
    def __init__(self) -> None:
        self._handlers: dict[type[Event], list[EventHandler]] = defaultdict(list)

    def push(self, event: Event) -> None:
        event_type = type(event)
        for handler in self._handlers[event_type]:
            handler(event)

    def register(self, handler: EventHandler) -> EventHandler:
        """Register an event handler.
        Can be used as a decorator.
        """
        event_type = handler.__annotations__["event"]
        self._handlers[event_type].append(handler)
        return handler


event_bus = _EventBus()
