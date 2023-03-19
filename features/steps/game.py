from behave import then, when

import yahtzee.commands as cmds
from yahtzee.app import execute, views
from yahtzee.events import ErrorRaised


@when("{player_name} rolls the dices")
def roll_dices(context, player_name: str):
    cmd = cmds.RollDices(context.game_uuid, player_name)
    execute(cmd)


@when("{player_name} rerolls the dices")
def reroll_dices(context, player_name: str):
    context.old_dices = views(context.game_uuid).dices
    roll_dices(context, player_name)


@when("{player_name} scores the {category} line")
def scores(context, player_name: str, category: str):
    cmd = cmds.Score(context.game_uuid, player_name, category)
    execute(cmd)


@when("{player_name} keeps the dices {dices}")
def keep_dices(context, player_name: str, dices: str):
    dices_numbers = [int(s) for s in dices if s.isdigit()]
    for dice in dices_numbers:
        cmd = cmds.KeepDice(context.game_uuid, player_name, dice)
        execute(cmd)


@when("the last round is played")
def last_round(context):
    players = views(context.game_uuid).players
    for category in (
        "Aces",
        "Twos",
        "Threes",
        "Fours",
        "Fives",
        "Sixes",
        "Three Of A Kind",
        "Four Of A Kind",
        "Full House",
        "Small Straight",
        "Large Straight",
        "Yahtzee",
        "Chance",
    ):
        for player in players:
            roll_dices(context, player["name"])
            scores(context, player["name"], category)


@then("it's {player_name}'s turn to play")
def check_turn(context, player_name: str):
    current_player = views(context.game_uuid).current_player
    assert current_player, "There is no current player"
    assert (
        current_player["name"] == player_name
    ), f"It's actually {current_player['name']}'s turn."


@then('An error said "{error_msg}"')
def error_raised(context, error_msg: str):
    logs = views(context.game_uuid).logs
    # We just search the error has been raised in the 10 last events
    for event in list(logs)[-10:]:
        if isinstance(event, ErrorRaised) and event.msg == error_msg:
            break
    else:
        assert False, f"Expected error `{error_msg}` did not raised"


@then("there was no error")
def no_error(context):
    logs = views(context.game_uuid).logs
    for event in list(logs):
        if isinstance(event, ErrorRaised):
            assert False, f"Unexpected error `{event.msg}` raised"


@then("{player_name} score is positive")
def score_is_positive(context, player_name: str):
    player = views(context.game_uuid).player(player_name)
    assert player
    total = player["scorecard"]["total"]
    assert total > 0, f"{player_name}'s score = {total}"


@then("dices {dices} have the same value as before")
def dices_have_same_value(context, dices: str):
    dices_numbers = [int(s) for s in dices if s.isdigit()]
    for dice_num in dices_numbers:
        dice = views(context.game_uuid).dice(dice_num)
        old_dice = next(
            dice for dice in context.old_dices if dice["number"] == dice_num
        )
        assert dice["value"] == old_dice["value"], f"{dice_num} has changed value"


@then("dices {dices} are on the track")
def dices_may_have_different_value(context, dices: str):
    dices_numbers = [int(s) for s in dices if s.isdigit()]
    for dice_num in dices_numbers:
        dice = views(context.game_uuid).dice(dice_num)
        assert dice["position"] == "on_the_track", f"{dice_num} is not on the track"


@then("the game is over")
def game_is_over(context):
    game_state = views(context.game_uuid).state
    assert game_state == "over", f"The game is not over but {game_state}"
