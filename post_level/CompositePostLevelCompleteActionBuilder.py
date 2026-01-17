from typing import List
from post_level.PostLevelCompleteAction import PostLevelCompleteAction
from post_level.CompositePostLevelCompleteAction import CompositePostLevelCompleteAction


class CompositePostLevelCompleteActionBuilder:
    def __init__(self):
        self.actions: List[PostLevelCompleteAction] = []

    def with_action(self, action: PostLevelCompleteAction) -> 'CompositePostLevelCompleteActionBuilder':
        self.actions.append(action)
        return self

    def build(self) -> CompositePostLevelCompleteAction:
        return CompositePostLevelCompleteAction(self.actions)
