from behave import then

from yahtzee.app import get_game


@then("it's {player_name}'s turn to play")
def check_turn(context, player_name: str):
    game = get_game(context.game_uuid)
    next_player = game.state.players.next
    assert (
        next_player.name == player_name
    ), f"it should be {player_name} to play but it is {next_player.name}"
