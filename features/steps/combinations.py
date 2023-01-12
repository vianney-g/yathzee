from behave import given, then

from yahtzee.dices import Combination, Dices


@given("the dices rolled {d1:d} {d2:d} {d3:d} {d4:d} {d5:d}")
def rolled_dices(context, d1: int, d2: int, d3: int, d4: int, d5: int):
    dices = [d1, d2, d3, d4, d5]
    context.dices = Dices(*dices)


@then("the {combination} score is {expected_score:d}")
def combination_score(context, combination: str, expected_score: int):
    dices: Dices = context.dices
    actual_score = Combination(combination).score(dices)
    assert (
        expected_score == actual_score
    ), f"Expected score {expected_score}, found {actual_score}"
