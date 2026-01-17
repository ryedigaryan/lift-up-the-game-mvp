from __future__ import annotations
import time
from typing import TYPE_CHECKING
from post_level.PostLevelCompleteAction import PostLevelCompleteAction
from GameHistoryPersistence import GameHistoryPersistence
from RawGameHistoryEntry import RawGameHistoryEntry

if TYPE_CHECKING:
    from Level import Level


class GameHistoryUpdaterAction(PostLevelCompleteAction):
    def __init__(self, level_num: int, persistence: GameHistoryPersistence):
        self.level_num = level_num
        self.persistence = persistence

    def execute(self, level: Level):
        """
        Saves the final score to the game history file.
        """
        level_name = f"level_{self.level_num}"
        final_penalty = level.status_bar.total_penalty
        entry = RawGameHistoryEntry(
            timestamp_epoch_seconds=int(time.time()),
            level=level_name,
            penalty=final_penalty
        )
        self.persistence.append(entry)
        print(f"Level {level_name} complete! Final penalty: {final_penalty:.2f} saved to history.")
