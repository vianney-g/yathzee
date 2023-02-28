"""Dices and combinations"""
import dataclasses
from collections.abc import Iterable, Iterator
from enum import Enum, IntEnum
from itertools import groupby
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

    @staticmethod
    def sum(dices: Iterable["Dice"]) -> int:
        return sum(dice.value for dice in dices)


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

    def score(self, dices: "Dices") -> Score:
        """Give the score for the combination according to a set of dices"""
        score: Score
        match self:
            case Combination.ACES:
                score = Dice.sum(dices.aces)
            case Combination.TWOS:
                score = Dice.sum(dices.twos)
            case Combination.THREES:
                score = Dice.sum(dices.threes)
            case Combination.FOURS:
                score = Dice.sum(dices.fours)
            case Combination.FIVES:
                score = Dice.sum(dices.fives)
            case Combination.SIXES:
                score = Dice.sum(dices.sixes)
            case Combination.THREE_OF_A_KIND:
                score = Dice.sum(dices.visibles) if dices.is_three_of_a_kind else 0
            case Combination.FOUR_OF_A_KIND:
                score = Dice.sum(dices.visibles) if dices.is_four_of_a_kind else 0
            case Combination.FULL_HOUSE:
                score = 25 if dices.is_full_house else 0
            case Combination.SMALL_STRAIGHT:
                score = 20 if dices.is_small_straight else 0
            case Combination.LARGE_STRAIGHT:
                score = 40 if dices.is_large_straight else 0
            case Combination.YAHTZEE:
                score = 50 if dices.is_yathzee else 0
            case Combination.CHANCE:
                score = Dice.sum(dices.visibles)
            case _:
                score = 0
        return score


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
        yield from (dice for dice in self.all if dice.is_on_the_table)

    @property
    def values(self) -> list[DiceValue]:
        return [dice.value for dice in self.visibles]

    def _visible_dices_of_value(self, value: DiceValue) -> Iterator[Dice]:
        return (dice for dice in self.visibles if dice.value == value)

    @property
    def aces(self) -> Iterator[Dice]:
        """ """
        return self._visible_dices_of_value(DiceValue.ONE)

    @property
    def twos(self) -> Iterator[Dice]:
        """ """
        return self._visible_dices_of_value(DiceValue.TWO)

    @property
    def threes(self) -> Iterator[Dice]:
        """ """
        return self._visible_dices_of_value(DiceValue.THREE)

    @property
    def fours(self) -> Iterator[Dice]:
        """ """
        return self._visible_dices_of_value(DiceValue.FOUR)

    @property
    def fives(self) -> Iterator[Dice]:
        """ """
        return self._visible_dices_of_value(DiceValue.FIVE)

    @property
    def sixes(self) -> Iterator[Dice]:
        """ """
        return self._visible_dices_of_value(DiceValue.SIX)

    @property
    def _visible_dices_groups_by_value(self) -> list[DicesSet]:
        sorted_dices = sorted(self.visibles)
        return [
            DicesSet(dices)
            for _, dices in groupby(sorted_dices, key=lambda dice: dice.value)
        ]

    @property
    def is_four_of_a_kind(self) -> bool:
        """A group of four dices with same value is in the set"""
        for dices in self._visible_dices_groups_by_value:
            if len(dices) >= 4:
                return True
        return False

    @property
    def is_three_of_a_kind(self) -> bool:
        """A group of three dices with same value is in the set"""
        for dices in self._visible_dices_groups_by_value:
            if len(dices) >= 3:
                return True
        return False

    @property
    def is_full_house(self) -> bool:
        """Dices can be grouped 3 of a value + 2 of a value"""
        groups = self._visible_dices_groups_by_value
        if len(groups) == 1:
            return True
        if len(groups) == 2:
            return len(groups[0]) in (2, 3)
        return False

    @property
    def is_large_straight(self) -> bool:
        """Five dices with incremental value"""
        valid_straights = [
            {1, 2, 3, 4, 5},
            {2, 3, 4, 5, 6},
        ]
        return set(self.values) in valid_straights

    @property
    def is_small_straight(self) -> bool:
        """Four dices with incremental value"""
        valid_straights = [
            {1, 2, 3, 4},
            {2, 3, 4, 5},
            {3, 4, 5, 6},
        ]

        uniq_dices = set(self.values)
        for straight in valid_straights:
            if straight.issubset(uniq_dices):
                return True
        return False

    @property
    def is_yathzee(self) -> bool:
        """Five dices of same value"""
        return len(set(self.values)) == 1
