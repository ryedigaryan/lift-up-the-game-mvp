import pygame as pg
from Floor import Floor
from Lift import Lift


class LiftUpGame:
    def __init__(self):
        pg.init()

        # Game constants
        self.NUM_FLOORS = 5
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.FLOOR_HEIGHT = self.SCREEN_HEIGHT // self.NUM_FLOORS

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

        self._initialize_game()

    def _initialize_game(self):
        """Initialize game objects"""
        # Calculate lift center position
        center_x = self.SCREEN_WIDTH // 2

        # Create floors (bottom to top)
        for i in range(self.NUM_FLOORS):
            floor = Floor(
                floor_number=i,
                y_position=(self.NUM_FLOORS - 1 - i) * self.FLOOR_HEIGHT,
                width=self.SCREEN_WIDTH,
                height=self.FLOOR_HEIGHT,
                total_floors=self.NUM_FLOORS,
                lift_center_x=center_x
            )
            self.floors.append(floor)

        # Create lifts in the horizontal center (pass floors for spawn location access)
        lift_a = Lift("A", center_x - 80, self.NUM_FLOORS, self.FLOOR_HEIGHT, self.floors)
        lift_b = Lift("B", center_x + 20, self.NUM_FLOORS, self.FLOOR_HEIGHT, self.floors)

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
        # Check all floors for customer clicks
        for floor in self.floors:
            customer = floor.handle_click(mouse_pos)
            if customer and customer.selected_lift:
                # Add customer to the selected lift
                for lift in self.lifts:
                    if lift.name == customer.selected_lift:
                        lift.add_customer_request(customer)
                        break

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

        # Clean up delivered customers periodically
        for floor in self.floors:
            floor.remove_delivered_customers()

        # Update active popup based on mouse position
        self._update_active_popup()

    def _update_active_popup(self):
        """Update which popup is active based on mouse position"""
        mouse_pos = pg.mouse.get_pos()

        # Check if mouse is still over the current active popup
        if self.active_popup_customer:
            if self.active_popup_customer.is_mouse_over_popup(mouse_pos):
                return  # Keep current active popup
            else:
                # Mouse left the popup
                self.active_popup_customer = None

        # Check if mouse entered any popup
        for floor in self.floors:
            for customer in floor.get_all_customers():
                if customer.is_mouse_over_popup(mouse_pos):
                    self.active_popup_customer = customer
                    return

    def draw(self):
        """Draw everything"""
        # Clear screen
        self.screen.fill((30, 30, 30))

        # Draw floors (without popups)
        for floor in self.floors:
            floor.draw(self.screen, draw_popups=False)

        # Draw lifts
        for lift in self.lifts:
            lift.draw(self.screen)

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
