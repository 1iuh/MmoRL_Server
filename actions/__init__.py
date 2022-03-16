from consts import INSTRUCT
from actions.move import Move
from actions.actions import Action


def action_factory(instruct, *args):
    if instruct == INSTRUCT.MOVE: return Move(*args)
