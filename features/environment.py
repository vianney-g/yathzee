from yahtzee.model import Player


def before_scenario(context, scenario):
    players: list[Player] = []
    context.players = players
