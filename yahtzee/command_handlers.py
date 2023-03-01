import logging
from collections.abc import Callable
from functools import singledispatch, wraps
from typing import Any

from . import commands as cmd
from .game import Game
from .game import events as evt
from .game.board import GameStatus, Player
from .game.dices import Combination, DiceNumber, DicePosition
from .game.score import Category
from .result import Err, Ok, Result

logger = logging.getLogger(__name__)

Handler = Callable[[Any, Game], Result]


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


def _validator(validator: Handler) -> Callable[[Handler], Handler]:
    def wrap(handler: Handler) -> Handler:
        @wraps(handler)
        def _wrapped(command, game, /) -> Result:
            validation = validator(command, game)
            match validation:
                case Ok():
                    return handler(command, game)
                case Err():
                    return validation

        return _wrapped

    return wrap


@_validator
def _player_can_play(command: cmd.PlayerCommand, game, /) -> Result:
    player = game.board.get_player(command.player)
    if player is not game.board.playing_player:
        return Err(f"{command.player}, it's not your turn to play")
    return Ok()


@_started.register
@_player_can_play
def roll_dice(_: cmd.RollDices, game: Game, /) -> Result:
    dices = game.board.dices.roll()
    for dice in dices.all:
        game.append(
            evt.DicePositionChanged(dice.number.value, dice.position.value, dice.points)
        )
    return Ok()


@_started.register
@_player_can_play
def score(command: cmd.Score, game: Game, /) -> Result:
    dices = game.board.dices
    if not dices.all_on_the_table:
        return Err("You must roll the dices first")

    player = game.board.get_player(command.player)
    category = Category(command.combination)
    if not player.can_score(category):
        return Err(f"{command.player}, you already scored {category.value}")

    combination = Combination(command.combination)
    score = dices.score(combination)

    game.append(evt.PointsScored(command.player, category.value, score))

    next_round = game.board.round.next_round()
    game.append(
        evt.TurnChanged(
            new_player=next_round.current_player.name,
            round_number=next_round.number,
        )
    )
    return Ok()


@_started.register
@_player_can_play
def keep_dice(command: cmd.KeepDice, game: Game, /) -> Result:
    dice = game.board.dices.get(DiceNumber(command.dice))
    game.append(
        evt.DicePositionChanged(
            dice.number.value, DicePosition.ASIDE.value, dice.points
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
