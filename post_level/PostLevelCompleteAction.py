from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Level import Level


class PostLevelCompleteAction(ABC):
    @abstractmethod
    def execute(self, level: Level):
        """
        Executes the action that should occur after a level is completed.

        Args:
            level (Level): The level object that has just been completed.
        """
        pass
