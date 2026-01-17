import pygame as pg
import csv
from Floor import Floor
from Lift import Lift
from StatusBar import StatusBar
from FileCustomerFactory import FileCustomerFactory


class LiftUpGame:
    def __init__(self):
        pg.init()

        # Game constants
        self.NUM_FLOORS = 5
        self.SCREEN_WIDTH = 800
        self.TOP_PADDING = 50
        self.GAME_HEIGHT = 800
        self.STATUS_BAR_HEIGHT = 100
        self.SCREEN_HEIGHT = self.GAME_HEIGHT + self.STATUS_BAR_HEIGHT + self.TOP_PADDING
        self.FLOOR_HEIGHT = self.GAME_HEIGHT // self.NUM_FLOORS

        # Screen setup
        self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pg.display.set_caption("Lift Up Game")

        # Clock
        self.clock = pg.time.Clock()
        self.fps = 60

        # Game objects
        self.floors = []
        self.lifts = []
        self.active_popup_customer = None
        self.status_bar = StatusBar(self.SCREEN_WIDTH, self.STATUS_BAR_HEIGHT, 0, self.GAME_HEIGHT + self.TOP_PADDING)
        
        # Load level data
        self.level_path = "data/level_1"
        self.file_factory = FileCustomerFactory(f"{self.level_path}/customer_spawns.csv")
        self.spawn_locations_data = self._load_spawn_locations(f"{self.level_path}/spawn_locations.csv")

        self._initialize_game()

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

    def _initialize_game(self):
        """Initialize game objects"""
        center_x = self.SCREEN_WIDTH // 2

        # Create floors
        for i in range(self.NUM_FLOORS):
            y_pos = self.TOP_PADDING + (self.NUM_FLOORS - 1 - i) * self.FLOOR_HEIGHT
            floor_spawn_data = self.spawn_locations_data.get(i)
            
            floor = Floor(
                floor_number=i,
                y_position=y_pos,
                width=self.SCREEN_WIDTH,
                height=self.FLOOR_HEIGHT,
                total_floors=self.NUM_FLOORS,
                lift_center_x=center_x,
                file_factory=self.file_factory,
                spawn_locations_data=floor_spawn_data
            )
            self.floors.append(floor)

        # Create lifts
        lift_a = Lift("A", center_x - 80, self.NUM_FLOORS, self.FLOOR_HEIGHT, self.floors, self.TOP_PADDING)
        lift_b = Lift("B", center_x + 20, self.NUM_FLOORS, self.FLOOR_HEIGHT, self.floors, self.TOP_PADDING)
        self.lifts.extend([lift_a, lift_b])

    def handle_events(self):
        """Handle pygame events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False

            if event.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = pg.mouse.get_pos()
                self._handle_click(mouse_pos)

        return True

    def _handle_click(self, mouse_pos):
        """Handle mouse clicks"""
        if self.active_popup_customer:
            if self.active_popup_customer.handle_click(mouse_pos):
                if self.active_popup_customer.selected_lift:
                    for lift in self.lifts:
                        if lift.name == self.active_popup_customer.selected_lift:
                            lift.add_customer_request(self.active_popup_customer)
                            break
                    self.active_popup_customer.is_active = False
                    self.active_popup_customer = None
                return

    def update(self, dt):
        """Update game state"""
        lift_positions = {lift.name: lift.x + lift.width // 2 for lift in self.lifts}

        for floor in self.floors:
            floor.update(dt, lift_positions)

        for lift in self.lifts:
            lift.update(dt)

        for floor in self.floors:
            self._process_delivered_customers(floor)

        self._update_active_popup()

    def _process_delivered_customers(self, floor):
        """Process delivered customers to calculate penalty and remove them"""
        for spawn_loc in floor.spawn_locations:
            for customer in spawn_loc.spawned_customers:
                if customer.state == "delivered" and customer.delivery_time is not None:
                    penalty = customer.calculate_penalty(customer.delivery_time)
                    self.status_bar.add_penalty(penalty)
            spawn_loc.remove_delivered_customers()
            
        for customer in floor.arrived_customers:
            if customer.state == "delivered" and customer.delivery_time is not None:
                penalty = customer.calculate_penalty(customer.delivery_time)
                self.status_bar.add_penalty(penalty)
        
        floor.arrived_customers = [c for c in floor.arrived_customers if c.state != "delivered"]

    def _update_active_popup(self):
        """Update which popup is active based on mouse position"""
        mouse_pos = pg.mouse.get_pos()

        if self.active_popup_customer:
            if self.active_popup_customer.is_mouse_over_popup(mouse_pos):
                return
            else:
                self.active_popup_customer.is_active = False
                self.active_popup_customer = None
        else:
            for floor in self.floors:
                for customer in floor.get_all_customers():
                    if customer.is_mouse_over_popup(mouse_pos):
                        self.active_popup_customer = customer
                        self.active_popup_customer.is_active = True
                        return

    def draw(self):
        """Draw everything"""
        self.screen.fill((30, 30, 30))

        for lift in self.lifts:
            lift.draw(self.screen)

        for floor in self.floors:
            floor.draw(self.screen, draw_popups=False)

        for floor in self.floors:
            for customer in floor.get_all_customers():
                if customer != self.active_popup_customer and customer.state != "in_lift":
                    customer.draw(self.screen, customer.y, draw_popup=True)

        if self.active_popup_customer:
            self.active_popup_customer.draw(self.screen, self.active_popup_customer.y, draw_popup=True)

        game_time = pg.time.get_ticks() / 1000.0
        font = pg.font.Font(None, 24)
        time_text = font.render(f"Time: {game_time:.1f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (self.SCREEN_WIDTH - 120, 10))
        
        self.status_bar.draw(self.screen)

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
