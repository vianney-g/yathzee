from behave import then, when

from yahtzee.app import execute, views
from yahtzee.commands import RollDices, Score
from yahtzee.events import ErrorRaised


@then("it's {player_name}'s turn to play")
def check_turn(context, player_name: str):
    current_player = views(context.game_uuid).current_player
    assert current_player, "There is no current player"
    assert (
        current_player["name"] == player_name
    ), f"It's actually {current_player['name']}'s turn."


@when("{player_name} rolls the dices")
def launch_dices(context, player_name: str):
    cmd = RollDices(context.game_uuid, player_name)
    execute(cmd)


@when("{player_name} scores the {category} line")
def scores(context, player_name: str, category: str):
    cmd = Score(context.game_uuid, player_name, category)
    execute(cmd)


@then('An error said "{error_msg}"')
def error_raised(context, error_msg: str):
    logs = views(context.game_uuid).logs
    # We just search the error has been raised in the 10 last events
    for event in logs[-10:]:
        if isinstance(event, ErrorRaised) and event.msg == error_msg:
            break
    else:
        assert False, f"Expected error `{error_msg}` did not raised"


@then("{player_name} score is positive")
def score_is_positive(context, player_name: str):
    player = views(context.game_uuid).player(player_name)
    assert player
    total = player["scorecard"]["total"]
    assert total > 0, f"{player_name}'s score = {total}"
