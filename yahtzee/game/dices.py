"""Dices and combinations"""
import dataclasses
from collections.abc import Iterator
from enum import Enum, IntEnum
from itertools import groupby
from random import choice

from .score import Score


class DiceValue(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6


DicesSet = list[DiceValue]


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
                score = sum(dices.aces)
            case Combination.TWOS:
                score = sum(dices.twos)
            case Combination.THREES:
                score = sum(dices.threes)
            case Combination.FOURS:
                score = sum(dices.fours)
            case Combination.FIVES:
                score = sum(dices.fives)
            case Combination.SIXES:
                score = sum(dices.sixes)
            case Combination.THREE_OF_A_KIND:
                score = sum(dices) if dices.is_three_of_a_kind else 0
            case Combination.FOUR_OF_A_KIND:
                score = sum(dices) if dices.is_four_of_a_kind else 0
            case Combination.FULL_HOUSE:
                score = 25 if dices.is_full_house else 0
            case Combination.SMALL_STRAIGHT:
                score = 20 if dices.is_small_straight else 0
            case Combination.LARGE_STRAIGHT:
                score = 40 if dices.is_large_straight else 0
            case Combination.YAHTZEE:
                score = 50 if dices.is_yathzee else 0
            case Combination.CHANCE:
                score = sum(dices)
            case _:
                score = 0
        return score


@dataclasses.dataclass(frozen=True)
class Dices:
    """A _hand_ of five dices"""

    dice_1: DiceValue
    dice_2: DiceValue
    dice_3: DiceValue
    dice_4: DiceValue
    dice_5: DiceValue

    @classmethod
    def roll(cls):
        values = list(DiceValue)
        return cls(
            choice(values),
            choice(values),
            choice(values),
            choice(values),
            choice(values),
        )

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
        """ """
        return self._dices_of_value(DiceValue.ONE)

    @property
    def twos(self) -> Iterator[DiceValue]:
        """ """
        return self._dices_of_value(DiceValue.TWO)

    @property
    def threes(self) -> Iterator[DiceValue]:
        """ """
        return self._dices_of_value(DiceValue.THREE)

    @property
    def fours(self) -> Iterator[DiceValue]:
        """ """
        return self._dices_of_value(DiceValue.FOUR)

    @property
    def fives(self) -> Iterator[DiceValue]:
        """ """
        return self._dices_of_value(DiceValue.FIVE)

    @property
    def sixes(self) -> Iterator[DiceValue]:
        """ """
        return self._dices_of_value(DiceValue.SIX)

    @property
    def _dices_groups_by_value(self) -> list[DicesSet]:
        sorted_dices = sorted(self)
        return [DicesSet(dices) for _, dices in groupby(sorted_dices)]

    @property
    def is_four_of_a_kind(self) -> bool:
        """A group of four dices with same value is in the set"""
        for dices in self._dices_groups_by_value:
            if len(dices) >= 4:
                return True
        return False

    @property
    def is_three_of_a_kind(self) -> bool:
        """A group of three dices with same value is in the set"""
        for dices in self._dices_groups_by_value:
            if len(dices) >= 3:
                return True
        return False

    @property
    def is_full_house(self) -> bool:
        """Dices can be grouped 3 of a value + 2 of a value"""
        groups = self._dices_groups_by_value
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
        return set(self) in valid_straights

    @property
    def is_small_straight(self) -> bool:
        """Four dices with incremental value"""
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
        """Five dices of same value"""
        return len(set(self)) == 1
