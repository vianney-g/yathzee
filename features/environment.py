from yahtzee.app import bootstrap, execute
from yahtzee.commands import CreateGame


def before_scenario(context, scenario):
    bootstrap()
    context.game_uuid = execute(CreateGame()).unwrap()["uuid"]
