from behave import given, when
from yahtzee.errors import YahtzeeError
from yahtzee.model import Game, Player, Players


@given("a player named {name}")
def create_player(context, name: str):
    player = Player(name)
    context.players.append(player)


@given("some players named")
def create_players(context):
    for row in context.table:
        create_player(context, row["name"])


@when("the game is created")
def create_game(context):
    try:
        context.game = Game(players=Players(context.players))
    except YahtzeeError as error:
        context.error = error
