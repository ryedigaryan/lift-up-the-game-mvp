from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level


class IfElseAction(PostLevelCompleteAction):
    def __init__(self, condition: Callable[[], bool], then_action: PostLevelCompleteAction, else_action: Optional[PostLevelCompleteAction] = None):
        """
        An action that executes one of two actions based on a condition.

        Args:
            condition (Callable[[], bool]): A function that returns True or False.
            then_action (PostLevelCompleteAction): The action to execute if the condition is True.
            else_action (Optional[PostLevelCompleteAction]): The action to execute if the condition is False.
        """
        self.condition = condition
        self.then_action = then_action
        self.else_action = else_action

    def execute(self, level: Level):
        """
        Executes the appropriate action based on the condition.
        """
        if self.condition():
            self.then_action.execute(level)
        elif self.else_action:
            self.else_action.execute(level)
