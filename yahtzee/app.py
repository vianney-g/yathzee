from functools import singledispatch
from logging import getLogger
from uuid import UUID

from .commands import Command, CreateGame, Err, GameCommand, Ok, Result
from .events import ErrorRaised
from .game import Game, GameViews
from .repository import InMemoryEventsStore, events, set_events_store

logger = getLogger(__name__)


def bootstrap() -> None:
    set_events_store(InMemoryEventsStore())


def get_game(uuid: UUID) -> Game:
    game_events = events().get_events(uuid)
    return Game.from_events(uuid, game_events)


def views(uuid: UUID) -> GameViews:
    game = get_game(uuid)
    return GameViews(game)


def commit_if_ok(result: Result, game: Game) -> None:
    match result:
        case Ok():
            game_events = events().get_events(game.uuid)
            events().add_events(game.uuid, game.events[len(game_events) :])
        case Err() as error:
            events().add_events(game.uuid, [ErrorRaised(error.err())])
            logger.error(result)


@singledispatch
def execute(command: Command, /) -> Result:
    return Err(f"Unknown command {command}")


@execute.register
def create_game(_: CreateGame, /) -> Result:
    game = Game.new()
    events().add_events(game.uuid, game.events)

    return Ok({"uuid": game.uuid})


@execute.register
def game_command(command: GameCommand, /) -> Result:
    game = get_game(command.game)
    result = game.execute(command)
    commit_if_ok(result, game)
    return result
