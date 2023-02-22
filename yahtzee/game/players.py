from dataclasses import dataclass, field

from .score import Category, Scorecard


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

    def can_score(self, category: Category) -> bool:
        return not self.scorecard.is_scored(category)

    @classmethod
    def nobody(cls) -> "Player":
        return _NOBODY_SENTINEL


_NOBODY_SENTINEL = Player("__NOBODY__")


Players = list[Player]
