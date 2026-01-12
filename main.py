import pygame as pg
from Floor import Floor
from Lift import Lift
from StatusBar import StatusBar


class LiftUpGame:
    def __init__(self):
        pg.init()

        # Game constants
        self.NUM_FLOORS = 5
        self.SCREEN_WIDTH = 800
        self.TOP_PADDING = 50  # Added padding to prevent popups going off-screen
        self.GAME_HEIGHT = 800
        self.STATUS_BAR_HEIGHT = 100
        self.SCREEN_HEIGHT = self.GAME_HEIGHT + self.STATUS_BAR_HEIGHT + self.TOP_PADDING
        
        # Adjust floor height calculation to account for padding
        self.FLOOR_HEIGHT = self.GAME_HEIGHT // self.NUM_FLOORS

        # Create screen
        self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pg.display.set_caption("Lift Up Game")

        # Clock for FPS
        self.clock = pg.time.Clock()
        self.fps = 60

        # Game objects
        self.floors = []
        self.lifts = []
        self.active_popup_customer = None  # Track which customer's popup is active
        self.status_bar = StatusBar(self.SCREEN_WIDTH, self.STATUS_BAR_HEIGHT, 0, self.GAME_HEIGHT + self.TOP_PADDING)

        self._initialize_game()

    def _initialize_game(self):
        """Initialize game objects"""
        # Calculate lift center position
        center_x = self.SCREEN_WIDTH // 2

        # Create floors (bottom to top)
        for i in range(self.NUM_FLOORS):
            # Add TOP_PADDING to all y-positions
            y_pos = self.TOP_PADDING + (self.NUM_FLOORS - 1 - i) * self.FLOOR_HEIGHT
            floor = Floor(
                floor_number=i,
                y_position=y_pos,
                width=self.SCREEN_WIDTH,
                height=self.FLOOR_HEIGHT,
                total_floors=self.NUM_FLOORS,
                lift_center_x=center_x
            )
            self.floors.append(floor)

        # Create lifts in the horizontal center (pass floors for spawn location access)
        lift_a = Lift("A", center_x - 80, self.NUM_FLOORS, self.FLOOR_HEIGHT, self.floors, self.TOP_PADDING)
        lift_b = Lift("B", center_x + 20, self.NUM_FLOORS, self.FLOOR_HEIGHT, self.floors, self.TOP_PADDING)

        self.lifts.append(lift_a)
        self.lifts.append(lift_b)

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
        # Only handle click for the active popup customer if one exists
        if self.active_popup_customer:
            if self.active_popup_customer.handle_click(mouse_pos):
                # If click was handled (lift selected), add request
                if self.active_popup_customer.selected_lift:
                    for lift in self.lifts:
                        if lift.name == self.active_popup_customer.selected_lift:
                            lift.add_customer_request(self.active_popup_customer)
                            break
                    # Clear active popup since customer is now waiting
                    self.active_popup_customer.is_active = False
                    self.active_popup_customer = None
                return

    def update(self, dt):
        """Update game state"""
        # Get lift positions for customer pathfinding
        lift_positions = {lift.name: lift.x + lift.width // 2 for lift in self.lifts}

        # Update floors and customers
        for floor in self.floors:
            floor.update(dt, lift_positions)

        # Update lifts
        for lift in self.lifts:
            lift.update(dt)

        # Clean up delivered customers periodically and calculate penalties
        for floor in self.floors:
            self._process_delivered_customers(floor)

        # Update active popup based on mouse position
        self._update_active_popup()

    def _process_delivered_customers(self, floor):
        """Process delivered customers to calculate penalty and remove them"""
        # We need to iterate through all customers on the floor to find delivered ones
        # This includes spawn locations and arrived customers
        
        # Check spawn locations
        for spawn_loc in floor.spawn_locations:
            for customer in spawn_loc.spawned_customers:
                if customer.state == "delivered" and customer.delivery_time is not None:
                    penalty = customer.calculate_penalty(customer.delivery_time)
                    self.status_bar.add_penalty(penalty)
            spawn_loc.remove_delivered_customers()
            
        # Check arrived customers
        for customer in floor.arrived_customers:
            if customer.state == "delivered" and customer.delivery_time is not None:
                penalty = customer.calculate_penalty(customer.delivery_time)
                self.status_bar.add_penalty(penalty)
        
        floor.arrived_customers = [c for c in floor.arrived_customers if c.state != "delivered"]

    def _update_active_popup(self):
        """Update which popup is active based on mouse position"""
        mouse_pos = pg.mouse.get_pos()

        # Check if mouse is still over the current active popup
        if self.active_popup_customer:
            if self.active_popup_customer.is_mouse_over_popup(mouse_pos):
                return  # Keep current active popup
            else:
                # Mouse left the popup
                self.active_popup_customer.is_active = False
                self.active_popup_customer = None
        else:
            # Check if mouse entered any popup
            for floor in self.floors:
                for customer in floor.get_all_customers():
                    if customer.is_mouse_over_popup(mouse_pos):
                        self.active_popup_customer = customer
                        self.active_popup_customer.is_active = True
                        return

    def draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill((30, 30, 30))

        # Draw lifts first (so customers appear in front)
        for lift in self.lifts:
            lift.draw(self.screen)

        # Draw floors (without popups)
        for floor in self.floors:
            floor.draw(self.screen, draw_popups=False)

        # Draw non-active popups first
        for floor in self.floors:
            for customer in floor.get_all_customers():
                if customer != self.active_popup_customer and customer.state != "in_lift":
                    customer.draw(self.screen, customer.y, draw_popup=True)

        # Draw active popup last (on top of everything)
        if self.active_popup_customer:
            self.active_popup_customer.draw(self.screen, self.active_popup_customer.y, draw_popup=True)

        # Draw game time
        game_time = pg.time.get_ticks() / 1000.0
        font = pg.font.Font(None, 24)
        time_text = font.render(f"Time: {game_time:.1f}s", True, (255, 255, 255))
        self.screen.blit(time_text, (self.SCREEN_WIDTH - 120, 10))
        
        # Draw status bar
        self.status_bar.draw(self.screen)

        # Update display
        pg.display.flip()

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            running = self.handle_events()

            # Update game state
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds
            self.update(dt)

            # Draw everything
            self.draw()

        pg.quit()


def main():
    game = LiftUpGame()
    game.run()


if __name__ == "__main__":
    main()
