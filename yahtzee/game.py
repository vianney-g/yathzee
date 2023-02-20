from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import singledispatch, singledispatchmethod
from logging import getLogger
from uuid import UUID, uuid4

from yahtzee.dices import Combination, Dices

from . import commands as cmd
from . import events as evt
from .commands import Err, Ok, Result
from .score import Category, Scorecard

logger = getLogger(__name__)


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
        return self is NOBODY_SENTINEL

    def is_playing(self, board: "Board") -> bool:
        """Return True if it's player's turn"""
        return self is board.round.current_player

    @classmethod
    def nobody(cls) -> "Player":
        return NOBODY_SENTINEL


NOBODY_SENTINEL = Player("__NOBODY__")


Players = list[Player]
RoundNumber = int


@dataclass(frozen=True)
class PlayerTurn:
    player: Player
    attempted_rolls: int = 0

    def roll(self):
        raise NotImplementedError

    def __bool__(self) -> bool:
        return bool(self.player)

    @classmethod
    def end_of_round(cls):
        return cls(Player.nobody())


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
            return cls(number, PlayerTurn.end_of_round(), players)

        if current_player is None:
            current_player = players[0]

        return cls(number, PlayerTurn(current_player), players)

    def next_round(self) -> "Round":
        player_index = self._players.index(self.current_player)
        try:
            next_player = self._players[player_index + 1]
        except IndexError:
            round = self.__class__.from_players(self._players, self.number + 1)
        else:
            player_turn = PlayerTurn(next_player)
            round = self.__class__(self.number, player_turn, self._players)
        return round

    @property
    def is_ended(self) -> bool:
        return bool(self.player_turn)

    @property
    def current_player(self) -> Player:
        return self.player_turn.player

    @classmethod
    def zero(cls) -> "Round":
        return cls(0, PlayerTurn.end_of_round(), [])


class GameStatus(Enum):
    NEW = "new"
    PENDING = "pending"
    STARTED = "started"
    OVER = "over"

    def execute(self, command: cmd.Command, game: "Game") -> Result:
        return _STATES[self](command, game)


@dataclass
class Board:
    players: Players
    status: GameStatus
    round: Round
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
            dices=Dices.roll(),
            game_id=UUID(int=0),
            version=0,
        )

    @singledispatchmethod
    def apply(self, event: evt.Event, /) -> None:
        logger.warning("Unapplyable event %s", event)

    @apply.register
    def game_created(self, event: evt.GameCreated, /):
        self.game_id = event.uuid
        self.status = GameStatus.PENDING

    @apply.register
    def player_added(self, event: evt.PlayerAdded, /):
        self.players.append(Player(event.player))
        self.inc_version()

    def get_player(self, player_name: str) -> Player:
        return next(player for player in self.players if player.name == player_name)

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
    def turn_changed(self, event: evt.TurnChanged):
        player = self.get_player(event.new_player)
        self.round = Round.from_players(self.players, event.round_number, player)
        self.inc_version()


@dataclass
class Game:
    uuid: UUID
    board: Board
    events: list[evt.Event] = field(default_factory=list)

    def append(self, event: evt.Event) -> None:
        self.board.apply(event)
        self.events.append(event)

    def execute(self, command: cmd.Command, /) -> Result:
        return self.board.status.execute(command, self)

    @classmethod
    def new(cls) -> "Game":
        new_uuid = uuid4()
        return Game.from_events(new_uuid, [])

    @classmethod
    def from_events(cls, uuid: UUID, events: list[evt.Event]) -> "Game":
        board = Board.new()
        for event in events:
            board.apply(event)
        return cls(uuid=uuid, board=board, events=events)


def _unhandled_command(command: cmd.Command) -> Result:
    logger.warning("Unhandled command %s", command)
    return Err(f"Unhandled command {command}")


@singledispatch
def _new(command: cmd.Command, _: Game, /) -> Result:
    return _unhandled_command(command)


@_new.register
def create_game(_: cmd.CreateGame, game: Game, /) -> Result:
    game.append(evt.GameCreated(game.uuid))
    return Ok({"uuid": game.uuid})


@singledispatch
def _pending(command: cmd.Command, _: Game, /) -> Result:
    return _unhandled_command(command)


@_pending.register
def add_player(command: cmd.AddPlayer, game: Game, /) -> Result:
    player = Player(command.name)
    if player in game.board.players:
        return Err(f"Player `{player}` is already in game")

    game.append(evt.PlayerAdded(command.name))
    return Ok()


@_pending.register
def start_game(_: cmd.StartGame, game: Game, /) -> Result:
    if not game.board.players:
        return Err("You can't start a game without any player")
    game.append(evt.GameStarted())
    return Ok()


@singledispatch
def _started(command: cmd.Command, _: Game, /) -> Result:
    return _unhandled_command(command)


def _assert_its_player_turn(command: cmd.PlayerCommand, game: Game) -> Result:
    player = game.board.get_player(command.player)
    if player.is_playing(game.board):
        return Ok()
    return Err(f"{command.player}, it's not your turn to play")


@_started.register
def roll_dice(command: cmd.RollDices, game: Game, /) -> Result:
    return _assert_its_player_turn(command, game)


@_started.register
def score(command: cmd.Score, game: Game, /) -> Result:
    its_player_turn = _assert_its_player_turn(command, game)
    if its_player_turn.is_err():
        return its_player_turn

    category = Category(command.category)
    combination = Combination(command.category)
    score = combination.score(game.board.dices)

    game.append(evt.PointsScored(command.player, category.value, score))
    next_round = game.board.round.next_round()
    game.append(
        evt.TurnChanged(
            new_player=next_round.current_player.name,
            round_number=next_round.number,
        )
    )
    return Ok()


CommandHandler = Callable[[cmd.Command, Game], Result]

_STATES: dict[GameStatus, CommandHandler] = {
    GameStatus.NEW: _new,
    GameStatus.PENDING: _pending,
    GameStatus.STARTED: _started,
}
