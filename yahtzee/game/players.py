from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board import Board

from .score import Scorecard


@dataclass(frozen=True)
class Player:
    name: str
    scorecard: Scorecard = field(default_factory=Scorecard)

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def score(self) -> int:
        return self.scorecard.score

    def asdict(self) -> dict:
        return {"name": self.name, "scorecard": self.scorecard.asdict()}

    def __bool__(self) -> bool:
        return self is _NOBODY_SENTINEL

    def is_playing(self, board: "Board") -> bool:
        """Return True if it's player's turn"""
        return self is board.round.current_player

    @classmethod
    def nobody(cls) -> "Player":
        return _NOBODY_SENTINEL


_NOBODY_SENTINEL = Player("__NOBODY__")


Players = list[Player]
