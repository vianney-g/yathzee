from dataclasses import dataclass
from enum import Enum
from functools import singledispatchmethod
from logging import getLogger
from typing import Union
from uuid import UUID

from . import events as evt
from .dices import Dice, Dices
from .players import Player, Players
from .score import Category

logger = getLogger(__name__)


@dataclass(frozen=True)
class PlayerTurn:
    player: Player
    attempted_rolls: int = 0

    def __bool__(self) -> bool:
        return bool(self.player)

    @classmethod
    def null(cls) -> "PlayerTurn":
        return cls(Player.nobody())

    @property
    def next_attempt(self) -> "PlayerTurn":
        if self.can_reroll:
            return self.__class__(self.player, self.attempted_rolls + 1)
        return self

    @property
    def can_reroll(self) -> bool:
        return self.attempted_rolls < 3


RoundNumber = int


class GameOver:
    current_player = Player.nobody()
    player_turn = PlayerTurn(current_player)

    def next_attempt(self) -> "GameOver":
        return self

    def next_round(self) -> "GameOver":
        return self


@dataclass(frozen=True)
class Round:
    """Single game round"""

    number: RoundNumber
    player_turn: PlayerTurn
    _players: Players

    @classmethod
    def from_players(
        cls,
        players: Players,
        number: RoundNumber = 1,
        current_player: Player | None = None,
    ) -> "Round":
        if not players:
            return cls(number, PlayerTurn.null(), players)

        if current_player is None:
            current_player = players[0]

        return cls(number, PlayerTurn(current_player), players)

    @property
    def _next_player(self) -> Player | None:
        player_index = self._players.index(self.current_player)
        try:
            return self._players[player_index + 1]
        except IndexError:
            return None

    def next_round(self) -> Union["Round", GameOver]:
        match (self._next_player):
            case None:
                if self.current_player.has_all_categories_scored:
                    return GameOver()
                return self.__class__.from_players(self._players, self.number + 1)
            case Player() as next_player:
                return self.__class__(
                    self.number, PlayerTurn(next_player), self._players
                )

    def next_attempt(self) -> "Round":
        return self.__class__(self.number, self.player_turn.next_attempt, self._players)

    def with_attempt(self, attempt_nb: int) -> "Round":
        return self.__class__(
            self.number, PlayerTurn(self.current_player, attempt_nb), self._players
        )

    @property
    def current_player(self) -> Player:
        return self.player_turn.player

    @classmethod
    def zero(cls) -> "Round":
        return cls(0, PlayerTurn.null(), [])

    @property
    def is_ended(self) -> bool:
        return isinstance(self.number, GameOver)


class GameStatus(Enum):
    NEW = "new"
    PENDING = "pending"
    STARTED = "started"
    OVER = "over"


@dataclass
class Board:
    players: Players
    status: GameStatus
    round: Round | GameOver
    dices: Dices
    game_id: UUID
    version: int

    def inc_version(self) -> None:
        self.version += 1

    @classmethod
    def new(cls) -> "Board":
        return cls(
            players=[],
            status=GameStatus.NEW,
            round=Round.zero(),
            dices=Dices.new_cup(),
            game_id=UUID(int=0),
            version=0,
        )

    @singledispatchmethod
    def apply(self, event: evt.Event, /) -> None:
        logger.warning("Unapplyable event %s", event)

    @apply.register
    def game_created(self, event: evt.GameCreated, /):
        self.game_id = event.game
        self.status = GameStatus.PENDING

    @apply.register
    def player_added(self, event: evt.PlayerAdded, /):
        self.players.append(Player(event.player))
        self.inc_version()

    def get_player(self, player_name: str) -> Player:
        return next(player for player in self.players if player.name == player_name)

    @property
    def playing_player(self) -> Player:
        return self.round.current_player

    @apply.register
    def game_started(self, _: evt.GameStarted, /):
        self.status = GameStatus.STARTED
        self.round = Round.from_players(self.players)
        self.inc_version()

    @apply.register
    def points_scored(self, event: evt.PointsScored):
        player = self.get_player(event.player)
        player.scorecard[Category(event.category)] = event.points
        self.inc_version()

    @apply.register
    def dice_changed(self, event: evt.DicePositionChanged):
        dice = Dice.from_literal(event.number, event.value, event.position)
        self.dices = self.dices.update(dice)
        self.inc_version()

    @apply.register
    def turn_changed(self, event: evt.TurnChanged):
        player = self.get_player(event.new_player)
        self.round = Round.from_players(self.players, event.round_number, player)
        self.inc_version()

    @apply.register
    def roll_performed(self, event: evt.RollPerformed):
        match self.round:
            case Round() as round:
                self.round = round.with_attempt(event.attempt_nb)
        self.inc_version()

    @apply.register
    def game_ended(self, _: evt.GameEnded, /):
        self.status = GameStatus.OVER
        self.inc_version()
