import pygame as pg
from Level import Level
from LevelsLoader import LevelsLoader
from post_level.GameHistoryUpdaterAction import GameHistoryUpdaterAction
from post_level.CompositePostLevelCompleteActionBuilder import CompositePostLevelCompleteActionBuilder


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

        # Initialize LevelsLoader
        self.levels_loader = LevelsLoader("data/levels")
        
        # Load the first level
        level_name = "level_1"
        raw_level_data = self.levels_loader.load(level_name)
        
        # Create post-level actions
        post_level_actions = (CompositePostLevelCompleteActionBuilder()
                              .with_action(GameHistoryUpdaterAction(level_name))
                              .build())
        
        # Initialize Level
        self.current_level = Level(
            raw_data=raw_level_data,
            screen_width=self.SCREEN_WIDTH,
            game_height=self.GAME_HEIGHT,
            top_padding=self.TOP_PADDING,
            status_bar_height=self.STATUS_BAR_HEIGHT,
            post_level_action=post_level_actions
        )

    def handle_events(self) -> bool:
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.current_level.handle_click(mouse_pos)

        return True

    def update(self, dt: float):
        """Update game state"""
        self.current_level.update(dt)

    def draw(self):
        """Draw everything"""
        self.screen.fill((30, 30, 30))
        
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
            dt = self.clock.tick(self.fps) / 1000.0
            self.update(dt)
            self.draw()
        pg.quit()
