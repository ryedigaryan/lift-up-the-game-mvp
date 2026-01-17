import pygame as pg
from Level import Level
from LevelsLoader import LevelsLoader
from GameHistoryPersistence import GameHistoryPersistence
from post_level.GameHistoryUpdaterAction import GameHistoryUpdaterAction
from post_level.CompositePostLevelCompleteAction import CompositePostLevelCompleteAction
from post_level.LoadLevelAction import LoadLevelAction
from post_level.LevelSelectionAction import LevelSelectionAction
from post_level.LevelTransitionAction import LevelTransitionAction
from post_level.GameHistoryShowAction import GameHistoryShowAction
from post_level.ExitAction import ExitAction


class LiftUpGame:
    def __init__(self):
        pg.init()

        # Game constants
        self.SCREEN_WIDTH = 800
        self.TOP_PADDING = 50
        self.GAME_HEIGHT = 800
        self.STATUS_BAR_HEIGHT = 100
        self.SCREEN_HEIGHT = self.GAME_HEIGHT + self.STATUS_BAR_HEIGHT + self.TOP_PADDING

        # Screen setup
        self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pg.display.set_caption("Lift Up Game")
        
        self.game_history_persistence = GameHistoryPersistence("data/output")
        self.current_level = None
        self.has_exited = False
        self.load_and_set_level(LevelsLoader("data/levels"), 1)

    def load_and_set_level(self, levels_loader: LevelsLoader, level_num: int):
        """
        Loads all data for a given level number and sets it as the current level.
        """
        if not levels_loader.level_exists(level_num):
            print(f"Attempted to load level '{level_num}', but it does not exist or is incomplete. Game will end.")
            self.exit()
            return

        # Create post-level actions
        next_level_num = level_num + 1
        
        level_select_action = LevelSelectionAction(levels_loader, lambda num: LoadLevelAction(self, levels_loader, num))
        
        post_level_actions = CompositePostLevelCompleteAction([
            GameHistoryUpdaterAction(level_num, self.game_history_persistence),
            LevelTransitionAction(
                game=self,
                level_num=level_num,
                persistence=self.game_history_persistence,
                next_level_action=LoadLevelAction(self, levels_loader, next_level_num) if levels_loader.level_exists(next_level_num) else None,
                replay_action=LoadLevelAction(self, levels_loader, level_num),
                level_select_action=level_select_action,
                game_history_show_action=GameHistoryShowAction(self, self.game_history_persistence, level_select_action, ExitAction(self)),
                exit_action=ExitAction(self)
            )
        ])
        
        # Initialize Level
        self.current_level = Level(
            raw_data=levels_loader.load(level_num),
            screen_width=self.SCREEN_WIDTH,
            game_height=self.GAME_HEIGHT,
            top_padding=self.TOP_PADDING,
            status_bar_height=self.STATUS_BAR_HEIGHT,
            post_level_action=post_level_actions
        )

    def exit(self):
        """Signals the game to exit by setting the has_exited flag to True."""
        self.has_exited = True

    def handle_events(self):
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit()
            elif self.current_level and event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.current_level.handle_click(mouse_pos)

    def update(self):
        """Update game state"""
        if self.current_level:
            self.current_level.update()

    def draw(self):
        """Draw everything"""
        self.screen.fill((30, 30, 30))
        
        if self.current_level:
            self.current_level.draw(self.screen)
            
            # Draw level time
            font = pg.font.Font(None, 24)
            time_text = font.render(f"Time: {self.current_level.level_time:.1f}s", True, (255, 255, 255))
            self.screen.blit(time_text, (self.SCREEN_WIDTH - 120, 10))

        pg.display.flip()

    def run(self):
        """Main game loop"""
        while not self.has_exited:
            self.handle_events()
            self.update()
            self.draw()
        pg.quit()
