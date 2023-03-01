"""Dices and combinations"""
import dataclasses
from collections import Counter
from collections.abc import Callable, Iterator
from enum import Enum, IntEnum
from random import choice
from typing import Literal

from .score import Score


class DiceValue(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6

    @classmethod
    def random(cls) -> "DiceValue":
        values = list(DiceValue)
        return choice(values)


class DicePosition(Enum):
    IN_THE_CUP = "in_the_cup"
    ON_THE_TRACK = "on_the_track"
    ASIDE = "aside"


class DiceNumber(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


@dataclasses.dataclass(frozen=True)
class Dice:
    number: DiceNumber
    value: DiceValue
    position: DicePosition

    def __gt__(self, other: "Dice") -> bool:
        return self.value > other.value

    @property
    def is_in_the_cup(self) -> bool:
        return self.position is DicePosition.IN_THE_CUP

    @property
    def is_on_the_table(self) -> bool:
        return self.position is not DicePosition.IN_THE_CUP

    @classmethod
    def in_the_cup(cls, number: DiceNumber) -> "Dice":
        return cls(number, DiceValue.random(), DicePosition.IN_THE_CUP)

    @classmethod
    def from_literal(
        cls,
        number: Literal[1, 2, 3, 4, 5],
        value: Literal[1, 2, 3, 4, 5, 6],
        position: Literal["in_the_cup", "on_the_track", "aside"],
    ) -> "Dice":
        return cls(
            DiceNumber(number),
            DiceValue(value),
            DicePosition(position),
        )

    @property
    def points(self) -> Literal[1, 2, 3, 4, 5, 6]:
        return self.value.value

    def roll(self) -> "Dice":
        """Roll the dice.
        If the dice is not in the cup, it is not rolled.
        """
        if not self.is_in_the_cup:
            return self
        return self.__class__(
            self.number, DiceValue.random(), DicePosition.ON_THE_TRACK
        )


DicesSet = list[Dice]


class Combination(Enum):
    """Possible dices combinations"""

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

    def score(self, dices: list[DiceValue]) -> Score:
        """Return the score for the given combination"""
        return _COMBINATION_SCORES[self](dices)


def _sum_of(value: DiceValue) -> Callable[[list[DiceValue]], int]:
    """Return a function that sums the dices of a given value"""

    def _binded_sum(dices: list[DiceValue]) -> int:
        return sum(dice for dice in dices if dice == value)

    return _binded_sum


def is_three_of_a_kind(dices: list[DiceValue]) -> bool:
    """Check if the dices are three of a kind"""
    count_by_value = Counter(dices)
    return max(count_by_value.values()) >= 3


def is_four_of_a_kind(dices: list[DiceValue]) -> bool:
    """Check if the dices are four of a kind"""
    count_by_value = Counter(dices)
    return max(count_by_value.values()) >= 4


def is_full_house(dices: list[DiceValue]) -> bool:
    """Check if the dices are a full house"""
    count_by_value = Counter(dices)
    dices_set = set(dices)
    if len(dices_set) == 1:
        return True
    if len(dices_set) == 2 and max(count_by_value.values()) == 3:
        return True
    return False


def is_large_straight(dices: list[DiceValue]) -> bool:
    """Check if the dices are a large straight"""
    dices_set = set(dices)
    return any(straight.issubset(dices_set) for straight in LARGE_STRAIGHTS)


def is_small_straight(dices: list[DiceValue]) -> bool:
    """Check if the dices are a small straight"""
    dices_set = set(dices)
    return any(straight.issubset(dices_set) for straight in SMALL_STRAIGHTS)


def three_of_a_kind_score(dices: list[DiceValue]) -> int:
    """Return the score for three of a kind"""
    return sum(dices) if is_three_of_a_kind(dices) else 0


def four_of_a_kind_score(dices: list[DiceValue]) -> int:
    """Return the score for four of a kind"""
    return sum(dices) if is_four_of_a_kind(dices) else 0


def small_straight_score(dices: list[DiceValue]) -> int:
    """Return the score for a small straight"""
    return 20 if is_small_straight(dices) else 0


def large_straight_score(dices: list[DiceValue]) -> int:
    """Return the score for a large straight"""
    return 40 if is_large_straight(dices) else 0


def full_house_score(dices: list[DiceValue]) -> int:
    """Return the score for a full house"""
    return 25 if is_full_house(dices) else 0


def yahtzee_score(dices: list[DiceValue]) -> int:
    """Return the score for a yahtzee"""
    return 50 if len(set(dices)) == 1 else 0


SMALL_STRAIGHTS = ({1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6})
LARGE_STRAIGHTS = ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6})

_COMBINATION_SCORES: dict[Combination, Callable[[list[DiceValue]], int]] = {
    Combination.ACES: _sum_of(DiceValue.ONE),
    Combination.TWOS: _sum_of(DiceValue.TWO),
    Combination.THREES: _sum_of(DiceValue.THREE),
    Combination.FOURS: _sum_of(DiceValue.FOUR),
    Combination.FIVES: _sum_of(DiceValue.FIVE),
    Combination.SIXES: _sum_of(DiceValue.SIX),
    Combination.THREE_OF_A_KIND: three_of_a_kind_score,
    Combination.FOUR_OF_A_KIND: four_of_a_kind_score,
    Combination.FULL_HOUSE: full_house_score,
    Combination.SMALL_STRAIGHT: small_straight_score,
    Combination.LARGE_STRAIGHT: large_straight_score,
    Combination.YAHTZEE: yahtzee_score,
    Combination.CHANCE: sum,
}


@dataclasses.dataclass(frozen=True)
class Dices:
    """A _hand_ of five dices"""

    dice_1: Dice
    dice_2: Dice
    dice_3: Dice
    dice_4: Dice
    dice_5: Dice

    @classmethod
    def new_cup(cls) -> "Dices":
        dices = [Dice.in_the_cup(num) for num in DiceNumber]
        return cls(*dices)

    @property
    def all_on_the_table(self) -> bool:
        return all(dice.is_on_the_table for dice in self.all)

    @property
    def all(self) -> Iterator[Dice]:
        yield from (self.dice_1, self.dice_2, self.dice_3, self.dice_4, self.dice_5)

    def roll(self) -> "Dices":
        dices = [dice.roll() for dice in self.all]
        return self.__class__(*dices)

    def update(self, dice: Dice) -> "Dices":
        dices = [dice if _dice.number == dice.number else _dice for _dice in self.all]
        return self.__class__(*dices)

    @property
    def visibles(self) -> Iterator[Dice]:
        return (dice for dice in self.all if dice.is_on_the_table)

    @property
    def values(self) -> Iterator[DiceValue]:
        return (dice.value for dice in self.visibles)

    def score(self, combination: Combination) -> int:
        return combination.score(list(self.values))
