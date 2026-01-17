import pygame as pg
import csv
from Level import Level
from RawLevelData import RawLevelData


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

        # Load level data
        self.level_path = "data/level_1"
        spawn_locations_data = self._load_spawn_locations(f"{self.level_path}/spawn_locations.csv")
        raw_level_data = RawLevelData(
            customer_spawns_path=f"{self.level_path}/customer_spawns.csv",
            spawn_locations_data=spawn_locations_data,
            num_floors=5
        )
        
        # Initialize Level
        self.current_level = Level(
            raw_data=raw_level_data,
            screen_width=self.SCREEN_WIDTH,
            game_height=self.GAME_HEIGHT,
            top_padding=self.TOP_PADDING,
            status_bar_height=self.STATUS_BAR_HEIGHT
        )

    def _load_spawn_locations(self, file_path):
        """Loads spawn location data from a CSV file."""
        locations = {}
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    floor = int(row['Floor'])
                    x = int(row['X'])
                    if floor not in locations:
                        locations[floor] = []
                    locations[floor].append({'X': x})
        except FileNotFoundError:
            print(f"Error: Could not find spawn locations file {file_path}")
        except Exception as e:
            print(f"Error parsing spawn locations file: {e}")
        return locations

    def handle_events(self):
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self.current_level.handle_click(mouse_pos)

        return True

    def update(self, dt):
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


def main():
    game = LiftUpGame()
    game.run()


if __name__ == "__main__":
    main()
