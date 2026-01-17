from __future__ import annotations
from typing import TYPE_CHECKING
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level
    from LiftUpGame import LiftUpGame
    from LevelsLoader import LevelsLoader


class LoadLevelAction(PostLevelCompleteAction):
    def __init__(self, game: LiftUpGame, levels_loader: LevelsLoader, level_to_load: int):
        """
        An action that loads a specific level.

        Args:
            game (LiftUpGame): The main game instance.
            levels_loader (LevelsLoader): The loader for level data.
            level_to_load (int): The number of the level to load.
        """
        self.game = game
        self.levels_loader = levels_loader
        self.level_to_load = level_to_load

    def execute(self, level: Level):
        """
        Triggers the main game to load the specified level.
        """
        print(f"Loading level: {self.level_to_load}...")
        self.game.load_and_set_level(self.levels_loader, self.level_to_load)
