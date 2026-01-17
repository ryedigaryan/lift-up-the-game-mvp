from __future__ import annotations
from typing import TYPE_CHECKING
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level
    from LiftUpGame import LiftUpGame


class ExitAction(PostLevelCompleteAction):
    """
    An action that signals the game to exit.
    """
    def __init__(self, game: LiftUpGame):
        self.game = game

    def execute(self, level: Level):
        """
        Calls the main game's exit method.
        """
        self.game.exit()
