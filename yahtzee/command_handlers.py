import logging
from collections.abc import Callable
from functools import singledispatch

from . import commands as cmd
from . import events as evt
from .commands import Err, Ok, Result
from .dices import Combination
from .game import Game, GameStatus, Player
from .score import Category

logger = logging.getLogger(__name__)


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


def handle(game: Game, command: cmd.Command) -> Result:
    state_handler = _STATES[game.board.status]
    return state_handler(command, game)
