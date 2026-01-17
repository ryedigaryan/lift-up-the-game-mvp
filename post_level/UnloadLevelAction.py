from Level import Level
from post_level.PostLevelCompleteAction import PostLevelCompleteAction


class UnloadLevelAction(PostLevelCompleteAction):
    def __init__(self, game):
        self.game = game

    def execute(self, level: Level):
        self.game.current_level = None
