from __future__ import annotations
from typing import TYPE_CHECKING
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level
    from LiftUpGame import LiftUpGame
    from LevelsLoader import LevelsLoader


class LoadNextLevelAction(PostLevelCompleteAction):
    def __init__(self, game: LiftUpGame, levels_loader: LevelsLoader, current_level_num: int):
        """
        An action that loads the next level.

        Args:
            game (LiftUpGame): The main game instance.
            levels_loader (LevelsLoader): The loader for level data.
            current_level_num (int): The number of the level that was just completed.
        """
        self.game = game
        self.levels_loader = levels_loader
        self.current_level_num = current_level_num

    def execute(self, level: Level):
        """
        Triggers the main game to load the next level.
        """
        next_level_num = self.current_level_num + 1
        print(f"Current level complete. Loading next level: {next_level_num}...")
        self.game.load_and_set_level(next_level_num)
