from behave import then


@then("it's {player_name}'s turn to play")
def check_turn(context, player_name: str):
    leader = context.game.players.leader
    assert leader.name == player_name
