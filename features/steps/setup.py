from behave import given, then, when

from yahtzee.app import execute, views
from yahtzee.commands import AddPlayer, StartGame


@given("a player named {name}")
def create_player(context, name: str):
    add_player = AddPlayer(context.game_uuid, name)
    execute(add_player)


@given("no player")
def no_player(context):
    pass


@given("some players named")
def create_players(context):
    for row in context.table:
        add_player = AddPlayer(context.game_uuid, row["name"])
        execute(add_player)


@given("the game is started")
def start_game(context):
    execute(StartGame(context.game_uuid))


@when("the game is created")
def create_game(context):
    assert hasattr(context, "game_uuid")


@then("the game can not be started")
def game_cannot_start(context):
    start = StartGame(context.game_uuid)
    result = execute(start)
    assert result.is_err()


@then("just 1 player is in the game")
def one_player_in_the_game(context):
    players_nb = len(views(context.game_uuid).players)
    assert players_nb == 1, f"Expecting game to have 1 player, got {players_nb}"
