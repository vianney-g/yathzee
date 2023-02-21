from collections.abc import Iterable
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .board import Board
from .events import Event


@dataclass
class Game:
    uuid: UUID
    board: Board
    events: list[Event]
    new_events: list[Event] = field(default_factory=list)

    def append(self, event: Event) -> None:
        self.board.apply(event)
        self.new_events.append(event)

    @classmethod
    def new(cls) -> "Game":
        new_uuid = uuid4()
        return Game.from_events(new_uuid, [])

    @classmethod
    def from_events(cls, uuid: UUID, events: Iterable[Event]) -> "Game":
        board = Board.new()
        events = list(events)
        for event in events:
            board.apply(event)
        return cls(uuid=uuid, board=board, events=events)
