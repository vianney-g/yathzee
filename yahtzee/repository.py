from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Protocol
from uuid import UUID

from .events import SystemEvent
from .game.events import Event as GameEvent

Event = GameEvent | SystemEvent


class EventsStore(Protocol):
    def get_events(self, uuid: UUID) -> Iterable[Event]:
        ...

    def get_game_events(self, uuid: UUID) -> Iterable[GameEvent]:
        ...

    def add_events(self, uuid: UUID, events: Sequence[Event]) -> None:
        ...


class InMemoryEventsStore(EventsStore):
    def __init__(self) -> None:
        self._events: dict[UUID, list[Event]] = defaultdict(list)

    def get_events(self, uuid: UUID) -> list[Event]:
        return self._events[uuid]

    def get_game_events(self, uuid: UUID) -> Iterable[GameEvent]:
        for event in self.get_events(uuid):
            match event:
                case SystemEvent():
                    continue
                case GameEvent():
                    yield event

    def add_events(self, uuid: UUID, events: Sequence[Event]) -> None:
        self._events[uuid].extend(events)


_events: None | EventsStore = None


def set_events_store(repo: EventsStore) -> None:
    """Initialize the game repository"""
    global _events
    _events = repo


def events() -> EventsStore:
    if _events is None:
        raise RuntimeError(
            "Events Store was not initialized: call `set_events_store` first"
        )
    return _events
