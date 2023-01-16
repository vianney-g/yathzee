from collections import defaultdict
from typing import Protocol
from uuid import UUID

from .events import Event


class EventsStore(Protocol):
    def get_events(self, uuid: UUID) -> list[Event]:
        ...

    def add_events(self, uuid: UUID, events: list[Event]) -> None:
        ...


class InMemoryEventsStore(EventsStore):
    def __init__(self):
        self._events: dict[UUID, list[Event]] = defaultdict(list)

    def get_events(self, uuid: UUID) -> list[Event]:
        return self._events[uuid]

    def add_events(self, uuid: UUID, events: list[Event]) -> None:
        self._events[uuid].extend(events)


_events: None | EventsStore = None


def set_events_store(repo: EventsStore):
    """Initialize the game repository"""
    global _events
    _events = repo


def events() -> EventsStore:
    if _events is None:
        raise RuntimeError(
            "Events Store was not initialized: call `set_events_store` first"
        )
    return _events
