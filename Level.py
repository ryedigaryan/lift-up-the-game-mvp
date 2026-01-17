import pygame as pg
from Floor import Floor
from Lift import Lift
from StatusBar import StatusBar
from FileCustomerFactory import FileCustomerFactory


class Level:
    def __init__(self, raw_data, screen_width, game_height, top_padding, status_bar_height):
        """
        Represents a single game level.

        Args:
            raw_data (RawLevelData): The raw data for this level.
            screen_width (int): Width of the game screen.
            game_height (int): Height of the playable game area.
            top_padding (int): Padding at the top of the screen.
            status_bar_height (int): Height of the status bar.
        """
        self.raw_data = raw_data
        self.screen_width = screen_width
        self.game_height = game_height
        self.top_padding = top_padding
        self.status_bar_height = status_bar_height
        
        self.num_floors = raw_data.num_floors
        self.floor_height = self.game_height // self.num_floors
        
        # Game objects
        self.floors = []
        self.lifts = []
        self.active_popup_customer = None
        self.status_bar = StatusBar(self.screen_width, self.status_bar_height, 0, self.game_height + self.top_padding)
        
        # Load factories
        self.file_factory = FileCustomerFactory(raw_data.customer_spawns_path)
        
        self._initialize_level()

    def _initialize_level(self):
        """Initialize floors and lifts based on raw data."""
        center_x = self.screen_width // 2

        # Create floors
        for i in range(self.num_floors):
            y_pos = self.top_padding + (self.num_floors - 1 - i) * self.floor_height
            floor_spawn_data = self.raw_data.spawn_locations_data.get(i)
            
            floor = Floor(
                floor_number=i,
                y_position=y_pos,
                width=self.screen_width,
                height=self.floor_height,
                total_floors=self.num_floors,
                lift_center_x=center_x,
                file_factory=self.file_factory,
                spawn_locations_data=floor_spawn_data
            )
            self.floors.append(floor)

        # Create lifts (currently hardcoded to 2, but could be data-driven later)
        lift_a = Lift("A", center_x - 80, self.num_floors, self.floor_height, self.floors, self.top_padding)
        lift_b = Lift("B", center_x + 20, self.num_floors, self.floor_height, self.floors, self.top_padding)
        self.lifts.extend([lift_a, lift_b])

    def handle_click(self, mouse_pos):
        """Handle mouse clicks within the level."""
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
                return True
        return False

    def update(self, dt):
        """Update level state."""
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
        """Process delivered customers to calculate penalty and remove them."""
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
        """Update which popup is active based on mouse position."""
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

    def draw(self, screen):
        """Draw the level."""
        # Draw lifts first (so customers appear in front)
        for lift in self.lifts:
            lift.draw(screen)

        # Draw floors (without popups)
        for floor in self.floors:
            floor.draw(screen, draw_popups=False)

        # Draw non-active popups first
        for floor in self.floors:
            for customer in floor.get_all_customers():
                if customer != self.active_popup_customer and customer.state != "in_lift":
                    customer.draw(screen, customer.y, draw_popup=True)

        # Draw active popup last (on top of everything)
        if self.active_popup_customer:
            self.active_popup_customer.draw(screen, self.active_popup_customer.y, draw_popup=True)
        
        # Draw status bar
        self.status_bar.draw(screen)
