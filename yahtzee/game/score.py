import dataclasses
from collections.abc import Iterator
from enum import Enum

Score = int


class Category(Enum):
    ACES = "Aces"
    TWOS = "Twos"
    THREES = "Threes"
    FOURS = "Fours"
    FIVES = "Fives"
    SIXES = "Sixes"
    UPPER_SECTION_BONUS = "Upper Section Bonus"
    THREE_OF_A_KIND = "Three Of A Kind"
    FOUR_OF_A_KIND = "Four Of A Kind"
    FULL_HOUSE = "Full House"
    SMALL_STRAIGHT = "Small Straight"
    LARGE_STRAIGHT = "Large Straight"
    YAHTZEE = "Yahtzee"
    CHANCE = "Chance"
    YAHTZEE_BONUS = "Yahtzee Bonus"

    @staticmethod
    def top_section() -> set["Category"]:
        return {
            Category.ACES,
            Category.TWOS,
            Category.THREES,
            Category.FOURS,
            Category.FIVES,
            Category.SIXES,
            Category.UPPER_SECTION_BONUS,
        }


@dataclasses.dataclass(frozen=True)
class ScoreLine:
    category: Category
    score: Score | None = None

    @property
    def is_in_top_section(self) -> bool:
        return self.category in Category.top_section()

    @property
    def score_value(self) -> Score:
        return Score(0) if self.score is None else self.score

    @property
    def is_scored(self) -> bool:
        return self.score is not None


@dataclasses.dataclass(frozen=True)
class Scorecard:
    lines: dict[Category, ScoreLine] = dataclasses.field(default_factory=dict)

    def is_scored(self, category: Category):
        return self.lines[category].is_scored

    def __post_init__(self):
        for category in Category:
            self.lines[category] = ScoreLine(category)

    def __iter__(self) -> Iterator[ScoreLine]:
        return iter(self.lines.values())

    def __getitem__(self, category: Category) -> Score | None:
        return self.lines[category].score

    def __setitem__(self, category: Category, score: Score) -> None:
        assert category is not Category.UPPER_SECTION_BONUS
        self.lines[category] = ScoreLine(category, score)
        self._set_upper_section_bonus()

    def _set_upper_section_bonus(self) -> None:
        if self.lines[Category.UPPER_SECTION_BONUS].is_scored:
            return
        if self.upper_section_score >= 63:
            self.lines[Category.UPPER_SECTION_BONUS] = ScoreLine(
                Category.UPPER_SECTION_BONUS, Score(35)
            )

    @property
    def upper_section_score(self) -> Score:
        return sum(line.score_value for line in self if line.is_in_top_section)

    @property
    def score(self) -> Score:
        return sum(line.score_value for line in self)

    @property
    def is_complete(self) -> bool:
        return all(line.is_scored for line in self)

    def asdict(self) -> dict[str, int | None]:
        categories = {line.category.value: line.score for line in self}
        return {
            **categories,
            "upper_section_total": self.upper_section_score,
            "total": self.score,
        }
