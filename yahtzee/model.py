import dataclasses
from collections import Counter
from enum import Enum
from itertools import cycle, groupby
from typing import Iterator, Literal, Self

from .errors import YahtzeeError


@dataclasses.dataclass
class Player:
    name: str
    score: int = 0


class Players:
    def __init__(self, players: list[Player]):
        self._assert_players_are_valid(players)
        self.players = players
        self.turn_cycle = cycle(self.players)
        self.leader = next(self.turn_cycle)

    @classmethod
    def _assert_players_are_valid(cls, players: list[Player]):
        if not players:
            raise YahtzeeError("Can't create a game with no player")
        cls._assert_no_players_with_same_name(players)

    @classmethod
    def _assert_no_players_with_same_name(cls, players: list[Player]):
        name_count = Counter(player.name for player in players)
        most_common_name, count = name_count.most_common(1)[0]
        if count > 1:
            raise YahtzeeError(f"A player named {most_common_name} already exists")


@dataclasses.dataclass
class Game:
    players: Players


DiceValue = Literal[1, 2, 3, 4, 5, 6]
DicesSet = list[DiceValue]
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


class Combination(Enum):
    ACES = "Aces"
    TWOS = "Twos"
    THREES = "Threes"
    FOURS = "Fours"
    FIVES = "Fives"
    SIXES = "Sixes"
    THREE_OF_A_KIND = "Three Of A Kind"
    FOUR_OF_A_KIND = "Four Of A Kind"
    FULL_HOUSE = "Full House"
    SMALL_STRAIGHT = "Small Straight"
    LARGE_STRAIGHT = "Large Straight"
    YAHTZEE = "Yahtzee"
    CHANCE = "Chance"

    def score(self, dices: "Dices") -> Score:
        match self:
            case Combination.ACES:
                return sum(dices.aces)
            case Combination.TWOS:
                return sum(dices.twos)
            case Combination.THREES:
                return sum(dices.threes)
            case Combination.FOURS:
                return sum(dices.fours)
            case Combination.FIVES:
                return sum(dices.fives)
            case Combination.SIXES:
                return sum(dices.sixes)
            case Combination.THREE_OF_A_KIND:
                return sum(dices) if dices.is_three_of_a_kind else 0
            case Combination.FOUR_OF_A_KIND:
                return sum(dices) if dices.is_four_of_a_kind else 0
            case Combination.FULL_HOUSE:
                return 25 if dices.is_full_house else 0
            case Combination.SMALL_STRAIGHT:
                return 20 if dices.is_small_straight else 0
            case Combination.LARGE_STRAIGHT:
                return 40 if dices.is_large_straight else 0
            case Combination.YAHTZEE:
                return 50 if dices.is_yathzee else 0
            case Combination.CHANCE:
                return sum(dices)
            case _:
                return 0


@dataclasses.dataclass(frozen=True)
class Dices:
    dice_1: DiceValue
    dice_2: DiceValue
    dice_3: DiceValue
    dice_4: DiceValue
    dice_5: DiceValue

    def __iter__(self) -> Iterator[DiceValue]:
        yield self.dice_1
        yield self.dice_2
        yield self.dice_3
        yield self.dice_4
        yield self.dice_5

    def _dices_of_value(self, value: DiceValue) -> Iterator[DiceValue]:
        return (dice for dice in self if dice == value)

    @property
    def aces(self) -> Iterator[DiceValue]:
        return self._dices_of_value(1)

    @property
    def twos(self) -> Iterator[DiceValue]:
        return self._dices_of_value(2)

    @property
    def threes(self) -> Iterator[DiceValue]:
        return self._dices_of_value(3)

    @property
    def fours(self) -> Iterator[DiceValue]:
        return self._dices_of_value(4)

    @property
    def fives(self) -> Iterator[DiceValue]:
        return self._dices_of_value(5)

    @property
    def sixes(self) -> Iterator[DiceValue]:
        return self._dices_of_value(6)

    @property
    def dices_groups_by_value(self) -> list[DicesSet]:
        sorted_dices = sorted(self)
        return [DicesSet(dices) for _, dices in groupby(sorted_dices)]

    @property
    def is_four_of_a_kind(self) -> bool:
        for dices in self.dices_groups_by_value:
            if len(dices) >= 4:
                return True
        return False

    @property
    def is_three_of_a_kind(self) -> bool:
        for dices in self.dices_groups_by_value:
            if len(dices) >= 3:
                return True
        return False

    @property
    def is_full_house(self) -> bool:
        groups = self.dices_groups_by_value
        if len(groups) == 1:
            return True
        if len(groups) == 2:
            return len(groups[0]) in (2, 3)
        return False

    @property
    def is_large_straight(self) -> bool:
        valid_straights = [
            {1, 2, 3, 4, 5},
            {2, 3, 4, 5, 6},
        ]
        return set(self) in valid_straights

    @property
    def is_small_straight(self) -> bool:
        valid_straights = [
            {1, 2, 3, 4},
            {2, 3, 4, 5},
            {3, 4, 5, 6},
        ]

        uniq_dices = set(self)
        for straight in valid_straights:
            if straight.issubset(uniq_dices):
                return True
        return False

    @property
    def is_yathzee(self) -> bool:
        return len(set(self)) == 1
