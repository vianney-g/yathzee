from behave import given, then

from yahtzee.app import get_game
from yahtzee.game.game import Player
from yahtzee.game.score import Category, Score, Scorecard


@then("{player_name} score is equal to {score:d}")
def assert_score(context, player_name: str, score: int):
    game = get_game(context.game_uuid)
    player: Player = next(p for p in game.board.players if p.name == player_name)
    assert player.score == score, f"Unexpected score {score}"


@given("the following scorecard")
def create_scorecard(context):
    scorecard = Scorecard()
    for row in context.table:
        category = Category(row["category"])
        score = Score(row["score"])
        scorecard[category] = score
    context.scorecard = scorecard


@then("the total of scorecard is {expected_score:d}")
def assert_total_score(context, expected_score: int):
    score = context.scorecard.score
    assert (
        score == expected_score
    ), f"Unexpected total {score}, expected {expected_score}"


@then("the scorecard is complete")
def assert_scorecard_is_complete(context):
    assert context.scorecard.is_complete


@then("the scorecard is not complete")
def assert_scorecard_is_not_complete(context):
    assert not context.scorecard.is_complete
