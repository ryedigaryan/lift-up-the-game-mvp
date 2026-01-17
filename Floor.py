import pygame as pg
import random
from CustomerSpawnLocation import CustomerSpawnLocation


class Floor:
    def __init__(self, floor_number, y_position, width, height, total_floors, lift_center_x, file_factory=None, spawn_locations_data=None):
        """
        Initialize a floor

        Args:
            floor_number: The floor number (0-indexed)
            y_position: Y coordinate of the floor
            width: Width of the floor
            height: Height of the floor
            total_floors: Total number of floors in the game
            lift_center_x: X coordinate of the center between lifts
            file_factory: Optional FileCustomerFactory instance for file-based spawning
            spawn_locations_data: Optional list of RawSpawnLocationData objects for this floor
        """
        self.floor_number = floor_number
        self.y = y_position
        self.width = width
        self.height = height
        self.total_floors = total_floors
        self.file_factory = file_factory
        self.spawn_locations = []
        
        if spawn_locations_data:
            self._create_spawn_locations_from_data(spawn_locations_data)
        else:
            self._create_random_spawn_location(lift_center_x)
        
        # Customers that arrived from other floors
        self.arrived_customers = []

    def _create_spawn_locations_from_data(self, data):
        """Create spawn locations from a list of RawSpawnLocationData objects"""
        # Sort by X to assign IDs correctly
        sorted_data = sorted(data, key=lambda d: d.x)
        
        for i, loc_data in enumerate(sorted_data):
            spawn_id = f"{self.floor_number}-{i+1}"
            spawn_x = loc_data.x
            
            spawn_loc = CustomerSpawnLocation(
                spawn_id,
                self.floor_number,
                spawn_x,
                self.total_floors,
                self.width,
                file_factory=self.file_factory
            )
            self.spawn_locations.append(spawn_loc)

    def _create_random_spawn_location(self, lift_center_x):
        """Create a single random spawn location far from lifts (legacy)"""
        # Define exclusion zone around lifts (200 pixels wide)
        lift_zone_left = lift_center_x - 100
        lift_zone_right = lift_center_x + 100

        # Define safe margin from edges
        margin = 50

        # Create list of valid spawn positions (far from lifts)
        valid_positions = []

        # Left side positions
        for x in range(margin, int(lift_zone_left)):
            valid_positions.append(x)

        # Right side positions
        for x in range(int(lift_zone_right), self.width - margin):
            valid_positions.append(x)

        # Choose random position
        if valid_positions:
            spawn_x = random.choice(valid_positions)
        else:
            # Fallback if no valid positions
            spawn_x = margin

        spawn_id = f"{self.floor_number}-1"

        # Create spawn location
        spawn_loc = CustomerSpawnLocation(
            spawn_id,
            self.floor_number,
            spawn_x,
            self.total_floors,
            self.width,
            spawn_interval=1.0 + 10.0*(self.floor_number+1),
            start_time=(self.floor_number+1) * 2.0 + (self.floor_number+1),
            file_factory=self.file_factory
        )
        self.spawn_locations.append(spawn_loc)

    def update(self, dt, lift_positions):
        """Update floor and all spawn locations"""
        # Update spawn locations
        for spawn_loc in self.spawn_locations:
            spawn_loc.update(dt)

        # Update all customers
        for spawn_loc in self.spawn_locations:
            for customer in spawn_loc.get_active_customers():
                customer.update(lift_positions)
                
        # Update arrived customers
        for customer in self.arrived_customers:
            customer.update(lift_positions)

    def get_all_customers(self):
        """Get all customers on this floor"""
        all_customers = []
        for spawn_loc in self.spawn_locations:
            all_customers.extend(spawn_loc.get_active_customers())
        all_customers.extend(self.arrived_customers)
        return all_customers

    def get_spawn_location_x(self):
        """Get the x position of the spawn location on this floor"""
        if self.spawn_locations:
            return self.spawn_locations[0].spawn_x
        return self.width // 2

    def handle_click(self, mouse_pos):
        """Handle mouse clicks for customer popups"""
        for customer in self.get_all_customers():
            if customer.handle_click(mouse_pos):
                return customer
        return None
        
    def add_customer(self, customer):
        """Add a customer to this floor (e.g. arrived from lift)"""
        self.arrived_customers.append(customer)
        
    def remove_customer(self, customer):
        """Remove a customer from this floor"""
        # Try to remove from spawn locations
        for spawn_loc in self.spawn_locations:
            if customer in spawn_loc.spawned_customers:
                spawn_loc.spawned_customers.remove(customer)
                return
        
        # Try to remove from arrived_customers
        if customer in self.arrived_customers:
            self.arrived_customers.remove(customer)

    def draw(self, screen, draw_popups=False):
        """Draw the floor (popups drawn separately to be on top)"""
        if not draw_popups:
            # Draw floor platform
            floor_color = (150, 150, 150)
            pg.draw.rect(screen, floor_color, (0, self.y + self.height - 10, self.width, 10))

            # Draw floor number
            font = pg.font.Font(None, 24)
            text = font.render(f"Floor {self.floor_number}", True, (255, 255, 255))
            screen.blit(text, (10, self.y + 10))

            # Draw spawn location markers (semi-transparent squares)
            for spawn_loc in self.spawn_locations:
                # Create a surface with alpha channel
                square_size = 30
                square_surface = pg.Surface((square_size, square_size), pg.SRCALPHA)
                square_surface.fill((255, 255, 0, 50))  # Yellow with alpha=50
                # Center the square on the spawn location
                square_x = spawn_loc.spawn_x - square_size // 2
                square_y = self.y + self.height - square_size - 10
                screen.blit(square_surface, (square_x, square_y))
                
                # Draw ID
                id_font = pg.font.Font(None, 20)
                id_text = id_font.render(spawn_loc.id, True, (255, 255, 255))
                screen.blit(id_text, (square_x, square_y - 15))

            # Draw all customers on this floor (without popups)
            for customer in self.get_all_customers():
                if customer.state != "in_lift":
                    customer.draw(screen, self.y + self.height - 50, draw_popup=False)
        else:
            # Only draw popups
            for customer in self.get_all_customers():
                if customer.state != "in_lift":
                    customer.draw(screen, self.y + self.height - 50, draw_popup=True)

    def remove_delivered_customers(self):
        """Clean up delivered customers"""
        for spawn_loc in self.spawn_locations:
            spawn_loc.remove_delivered_customers()
            
        self.arrived_customers = [c for c in self.arrived_customers if c.state != "delivered"]
