import dataclasses
from collections.abc import Iterator
from enum import Enum
from functools import singledispatchmethod
from itertools import cycle
from logging import getLogger
from uuid import UUID, uuid4

from .commands import AddPlayer, Command, Err, Ok, Result, StartGame
from .events import Event, GameCreated, GameStarted, PlayerAdded
from .score import Scorecard

logger = getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class Player:
    name: str
    scorecard: Scorecard = dataclasses.field(default_factory=Scorecard)

    def __hash__(self) -> int:
        return hash(self.name)

    @property
    def score(self) -> int:
        return self.scorecard.score


class Players:
    def __init__(self) -> None:
        self._players: list[Player] = []
        self._turn_cycle: Iterator[Player] | None = None

    @property
    def next(self) -> Player:
        if self._turn_cycle is None:
            self._turn_cycle = cycle(self._players)
        return next(self._turn_cycle)

    def add(self, player: Player) -> None:
        self._players.append(player)

    def __contains__(self, player: Player) -> bool:
        return player in self._players

    def __len__(self) -> int:
        return len(self._players)

    def __iter__(self):
        return iter(self._players)


class GameStatus(Enum):
    START_UP = "start-up"
    STARTED = "started"
    OVER = "over"


@dataclasses.dataclass
class GameState:
    game_id: UUID | None = None
    version: int = 0
    players: Players = dataclasses.field(default_factory=Players)
    status: GameStatus = GameStatus.START_UP

    @singledispatchmethod
    def apply(self, event: Event, /) -> None:
        logger.warning("Unused event %s", event)

    @apply.register
    def game_created(self, event: GameCreated, /):
        self.game_id = event.uuid

    @apply.register
    def player_added(self, event: PlayerAdded, /):
        self.players.add(Player(event.player_name))
        self.version += 1

    @apply.register
    def game_started(self, _: GameStarted, /):
        self.state = GameStatus.STARTED
        self.version += 1


@dataclasses.dataclass
class Game:
    uuid: UUID
    state: GameState
    events: list[Event] = dataclasses.field(default_factory=list)

    def append(self, event: Event) -> None:
        self.state.apply(event)
        self.events.append(event)

    @singledispatchmethod
    def execute(self, command: Command, /) -> Result:
        logger.warning("Unhandled command %s", command)
        return Ok()

    @execute.register
    def add_player(self, command: AddPlayer, /) -> Result:
        if self.state.status is not GameStatus.START_UP:
            return Err("You can't add a player in an already started game")

        player = Player(command.player_name)
        if player in self.state.players:
            return Err(f"Player `{player}` is already in game")

        self.append(PlayerAdded(command.player_name))
        return Ok()

    @execute.register
    def start_game(self, _: StartGame, /) -> Result:
        if self.state.status is not GameStatus.START_UP:
            # idempotent call
            return Ok()
        if not self.state.players:
            return Err("You can't start a game without any player")
        self.append(GameStarted())
        return Ok()

    @classmethod
    def new(cls) -> "Game":
        uuid = uuid4()
        return Game.from_events(uuid, [GameCreated(uuid)])

    @classmethod
    def from_events(cls, uuid: UUID, events: list[Event]) -> "Game":
        game = cls(uuid, GameState())
        for event in events:
            game.append(event)
        return game
