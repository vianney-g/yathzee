import dataclasses
from abc import ABC
from typing import Generic, NoReturn, TypeVar
from uuid import UUID

T = TypeVar("T", covariant=True)  # success type
E = TypeVar("E", covariant=True)  # error type


class ResultError(Exception):
    """Error but Ok was expected"""


class Ok(Generic[T]):
    def __init__(self, value: T = True):
        self._value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self._value


class Err(Generic[E]):
    def __init__(self, value: E = True):
        self._value = value

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> NoReturn:
        raise ResultError(self._value)


Result = Ok[T] | Err[E]


class Command(ABC):
    """Send a command to yahtzee game"""


@dataclasses.dataclass(frozen=True)
class CreateGame(Command):
    pass


@dataclasses.dataclass(frozen=True)
class AddPlayer(Command):
    game: UUID
    player_name: str


@dataclasses.dataclass(frozen=True)
class StartGame(Command):
    game: UUID
