from __future__ import annotations
from typing import TYPE_CHECKING
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level


class NoopAction(PostLevelCompleteAction):
    """
    An action that does nothing. Used as a placeholder.
    """
    def execute(self, level: Level):
        print("No-op action executed. (Placeholder for future functionality)")
        pass
