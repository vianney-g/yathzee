from functools import singledispatch
from logging import getLogger
from uuid import UUID

from .command_handlers import handle
from .commands import Command, CreateGame, Err, GameCommand, Ok, Result
from .events import ErrorRaised
from .game.game import Game
from .repository import InMemoryEventsStore, events, set_events_store
from .views import GameViews

logger = getLogger(__name__)


def bootstrap() -> None:
    set_events_store(InMemoryEventsStore())


def get_game(uuid: UUID) -> Game:
    game_events = events().get_game_events(uuid)
    return Game.from_events(uuid, game_events)


def views(uuid: UUID) -> GameViews:
    return GameViews(uuid, events())


def commit(result: Result, game: Game) -> None:
    """Commit all game events according to a command result.
    If command result is an error, commit the error message alone.
    """
    match result:
        case Ok():
            # just save the new events generated by the command
            events().add_events(game.uuid, game.new_events)
        case Err() as error:
            events().add_events(game.uuid, [ErrorRaised(error.err())])
            logger.error(result)


@singledispatch
def execute(command: Command, /) -> Result:
    return Err(f"Unknown command {command}")


@execute.register
def create_game(command: CreateGame, /) -> Result:
    game = Game.new()
    result = handle(game, command)
    commit(result, game)
    return result


@execute.register
def game_command(command: GameCommand, /) -> Result:
    game = get_game(command.game)
    result = handle(game, command)
    commit(result, game)
    return result
