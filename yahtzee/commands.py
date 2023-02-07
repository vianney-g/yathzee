from abc import ABC
from dataclasses import dataclass
from typing import Any, Generic, NoReturn, TypeVar, overload
from uuid import UUID

T = TypeVar("T", covariant=True)  # success type
E = TypeVar("E", covariant=True)  # error type


class ResultError(Exception):
    """Error but Ok was expected"""


class Ok(Generic[T]):
    _value: T

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, value: T):
        ...

    def __init__(self, value: Any = True):
        self._value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value

    def err(self) -> None:
        return None


class Err(Generic[E]):
    _value: E

    @overload
    def __init__(self):
        ...

    @overload
    def __init__(self, value: E):
        ...

    def __init__(self, value: Any = True):
        self._value = value

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> NoReturn:
        raise ResultError(self._value)

    def err(self) -> E:
        return self._value


Result = Ok[T] | Err[E]


class Command(ABC):
    """Send a command to yahtzee game"""


@dataclass(frozen=True)
class CreateGame(Command):
    pass


@dataclass(frozen=True)
class GameCommand(Command):
    game: UUID


@dataclass(frozen=True)
class AddPlayer(GameCommand):
    player_name: str


@dataclass(frozen=True)
class StartGame(GameCommand):
    pass


@dataclass(frozen=True)
class RollDices(GameCommand):
    player_name: str


@dataclass(frozen=True)
class Score(GameCommand):
    player_name: str
    category: str
