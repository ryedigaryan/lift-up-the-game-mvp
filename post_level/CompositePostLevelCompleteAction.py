from __future__ import annotations
from typing import List, TYPE_CHECKING
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level


class CompositePostLevelCompleteAction(PostLevelCompleteAction):
    def __init__(self, actions: List[PostLevelCompleteAction]) -> None:
        """
        An action that holds and executes a list of other actions.

        Args:
            actions (List[PostLevelCompleteAction]): A list of action objects to execute.
        """
        self.actions = actions

    def execute(self, level: Level):
        """
        Executes all actions in the composite list.
        """
        for action in self.actions:
            action.execute(level)
