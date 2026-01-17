import pygame as pg
from Level import Level
from LevelsLoader import LevelsLoader
from post_level.GameHistoryUpdaterAction import GameHistoryUpdaterAction
from post_level.CompositePostLevelCompleteAction import CompositePostLevelCompleteAction
from post_level.LoadLevelAction import LoadLevelAction
from post_level.IfElseAction import IfElseAction
from post_level.GameHistoryShowAction import GameHistoryShowAction
from post_level.LevelTransitionAction import LevelTransitionAction


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

        # Clock
        self.clock = pg.time.Clock()
        self.fps = 60
        
        self.current_level = None
        self.load_and_set_level(LevelsLoader("data/levels"), 1)

    def load_and_set_level(self, levels_loader: LevelsLoader, level_num: int):
        """
        Loads all data for a given level number and sets it as the current level.
        """
        if not levels_loader.level_exists(level_num):
            print(f"Attempted to load level '{level_num}', but it does not exist or is incomplete. Game will end.")
            self.current_level = None
            return

        # Create post-level actions
        post_level_actions = CompositePostLevelCompleteAction([
            GameHistoryUpdaterAction(level_num),
            IfElseAction(
                condition=lambda: levels_loader.level_exists(level_num + 1),
                then_action=LevelTransitionAction(
                    self, 
                    levels_loader, 
                    level_num, 
                    LoadLevelAction(self, levels_loader, level_num + 1)
                ),
                else_action=GameHistoryShowAction()
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

    def handle_events(self) -> bool:
        """Handle pygame events"""
        if not self.current_level:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return False
            return True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.current_level.handle_click(mouse_pos)

        return True

    def update(self, dt: float):
        """Update game state"""
        if self.current_level:
            self.current_level.update(dt)

    def draw(self):
        """Draw everything"""
        self.screen.fill((30, 30, 30))
        
        if self.current_level:
            self.current_level.draw(self.screen)

        game_time = pg.time.get_ticks() / 1000.0
        font = pg.font.Font(None, 24)
        time_text = font.render(f"Time: {game_time:.1f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (self.SCREEN_WIDTH - 120, 10))

        pg.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            if not self.current_level:
                running = False # End game if no more levels

            dt = self.clock.tick(self.fps) / 1000.0
            self.update(dt)
            self.draw()
        pg.quit()
