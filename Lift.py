import pygame as pg


class Lift:
    def __init__(self, name, x, total_floors, floor_height, floors=None):
        """
        Initialize a lift

        Args:
            name: Lift identifier (e.g., "A" or "B")
            x: X coordinate of the lift
            total_floors: Total number of floors
            floor_height: Height of each floor in pixels
            floors: List of Floor objects (for getting spawn locations)
        """
        self.name = name
        self.x = x
        self.width = 60
        self.height = 80
        self.current_floor = 0
        self.target_floors = set()  # Set of floors to visit
        self.customers_inside = []  # Customers currently in the lift
        self.waiting_customers = {}  # floor -> list of customers waiting at that floor
        self.state = "idle"  # idle, waiting, moving_up, moving_down
        self.speed = 1.5  # pixels per frame
        self.total_floors = total_floors
        self.floor_height = floor_height
        self.y = self._floor_to_y(0)
        self.door_open = False
        self.door_timer = 0
        self.door_wait_time = 2.0  # seconds to wait with door open
        self.floors = floors or []  # Reference to floor objects

    def _floor_to_y(self, floor):
        """Convert floor number to Y position (align with floor bottom)"""
        ground_height = 10
        return (self.total_floors - 1 - floor) * self.floor_height + self.floor_height - ground_height - self.height

    def _y_to_floor(self):
        """Get current floor based on Y position"""
        for floor in range(self.total_floors):
            floor_y = self._floor_to_y(floor)
            if abs(self.y - floor_y) < 5:
                return floor
        return self.current_floor

    def add_customer_request(self, customer):
        """Add a customer request to this lift"""
        if customer.current_floor not in self.waiting_customers:
            self.waiting_customers[customer.current_floor] = []
        self.waiting_customers[customer.current_floor].append(customer)
        self.target_floors.add(customer.current_floor)

    def update(self, dt):
        """Update lift state and position"""
        if self.state == "idle":
            if self.target_floors:
                self._start_moving()

        elif self.state == "waiting":
            self.door_timer += dt
            if self.door_timer >= self.door_wait_time:
                self._close_door_and_continue()

        elif self.state in ["moving_up", "moving_down"]:
            self._move_towards_target()

    def _start_moving(self):
        """Start moving to next target floor"""
        if not self.target_floors:
            self.state = "idle"
            return

        # Find next floor to visit
        next_floor = self._get_next_floor()
        target_y = self._floor_to_y(next_floor)

        if abs(self.y - target_y) < 5:
            # Already at the floor
            self._arrive_at_floor()
        else:
            # Start moving
            if self.y > target_y:
                self.state = "moving_up"
            else:
                self.state = "moving_down"

    def _get_delivery_floors(self):
        """Get floors where customers inside need to be delivered"""
        return set(customer.target_floor for customer in self.customers_inside)

    def _get_next_floor(self):
        """Get the next floor to visit based on current direction"""
        if not self.target_floors:
            return self.current_floor

        sorted_floors = sorted(self.target_floors)
        delivery_floors = self._get_delivery_floors()

        # If we have customers inside, prioritize their delivery floors
        if delivery_floors:
            if self.state == "moving_up":
                # Continue up, only stop at delivery floors or pickup floors on the way
                floors_above = [f for f in sorted_floors if f > self.current_floor]
                if floors_above:
                    # Prefer delivery floors, but stop at pickup floors if they're on the way
                    delivery_above = [f for f in floors_above if f in delivery_floors]
                    if delivery_above:
                        return delivery_above[0]
                    # Only pickup if it's before the next delivery floor
                    next_delivery = min(delivery_floors) if delivery_floors else float('inf')
                    pickup_before_delivery = [f for f in floors_above if f < next_delivery]
                    if pickup_before_delivery:
                        return pickup_before_delivery[0]
                    return delivery_above[0] if delivery_above else next_delivery
                else:
                    # Change direction to deliver
                    return min(delivery_floors)
            elif self.state == "moving_down":
                # Continue down, only stop at delivery floors or pickup floors on the way
                floors_below = [f for f in sorted_floors if f < self.current_floor]
                if floors_below:
                    delivery_below = [f for f in floors_below if f in delivery_floors]
                    if delivery_below:
                        return delivery_below[-1]
                    # Only pickup if it's before the next delivery floor
                    next_delivery = max(delivery_floors) if delivery_floors else float('-inf')
                    pickup_before_delivery = [f for f in floors_below if f > next_delivery]
                    if pickup_before_delivery:
                        return pickup_before_delivery[-1]
                    return delivery_below[-1] if delivery_below else next_delivery
                else:
                    # Change direction to deliver
                    return max(delivery_floors)
            else:  # idle
                # Go to nearest delivery floor
                return min(delivery_floors, key=lambda f: abs(f - self.current_floor))

        # No customers inside, normal pickup behavior
        if self.state == "moving_up" or self.state == "idle":
            floors_above = [f for f in sorted_floors if f > self.current_floor]
            if floors_above:
                return floors_above[0]
            else:
                return sorted_floors[0]
        else:
            floors_below = [f for f in sorted_floors if f < self.current_floor]
            if floors_below:
                return floors_below[-1]
            else:
                return sorted_floors[-1]

    def _move_towards_target(self):
        """Move the lift towards the target floor"""
        next_floor = self._get_next_floor()
        target_y = self._floor_to_y(next_floor)

        if abs(self.y - target_y) < self.speed:
            self.y = target_y
            self._arrive_at_floor()
        else:
            if self.y > target_y:
                self.y -= self.speed
            else:
                self.y += self.speed

    def _arrive_at_floor(self):
        """Handle arrival at a floor"""
        self.current_floor = self._y_to_floor()
        self.door_open = True
        self.state = "waiting"
        self.door_timer = 0

        # Drop off customers
        customers_to_remove = []
        for customer in self.customers_inside:
            if customer.target_floor == self.current_floor:
                # Get the spawn location x for this floor
                target_spawn_x = self.x + self.width // 2  # Default to lift position
                if self.floors and self.current_floor < len(self.floors):
                    target_spawn_x = self.floors[self.current_floor].get_spawn_location_x()

                customer.exit_lift(self.current_floor, self.x + self.width // 2, target_spawn_x)
                
                # Add customer to the floor's arrived list
                if self.floors and self.current_floor < len(self.floors):
                    self.floors[self.current_floor].add_customer(customer)
                    
                customers_to_remove.append(customer)

        for customer in customers_to_remove:
            self.customers_inside.remove(customer)

        # Pick up customers
        if self.current_floor in self.waiting_customers:
            for customer in self.waiting_customers[self.current_floor]:
                if customer.state == "waiting_at_lift":
                    # Remove customer from the floor they were on
                    if self.floors and customer.current_floor < len(self.floors):
                        self.floors[customer.current_floor].remove_customer(customer)

                    customer.enter_lift()
                    self.customers_inside.append(customer)
                    # Add their target floor to our route
                    self.target_floors.add(customer.target_floor)

            # Remove customers who entered
            self.waiting_customers[self.current_floor] = [
                c for c in self.waiting_customers[self.current_floor]
                if c.state != "in_lift"
            ]

            if not self.waiting_customers[self.current_floor]:
                del self.waiting_customers[self.current_floor]

        # Remove current floor from targets only if no more waiting customers
        if self.current_floor not in self.waiting_customers:
            self.target_floors.discard(self.current_floor)

    def _has_customers_still_walking_to_current_floor(self):
        """Check if there are customers walking to this lift at the CURRENT floor"""
        if self.current_floor in self.waiting_customers:
            for customer in self.waiting_customers[self.current_floor]:
                if customer.state == "walking_to_lift":
                    return True
        return False

    def _close_door_and_continue(self):
        """Close door and continue to next floor"""
        # Don't close door if customers are still walking to THIS floor
        if self._has_customers_still_walking_to_current_floor():
            # Reset timer to keep waiting
            self.door_timer = 0
            return

        self.door_open = False

        if self.target_floors:
            self._start_moving()
        else:
            self.state = "idle"

    def draw(self, screen):
        """Draw the lift"""
        # Lift color based on name
        color = (100, 200, 100) if self.name == "A" else (200, 100, 100)

        # Draw lift shaft (light background)
        shaft_color = (200, 200, 200)
        for floor in range(self.total_floors):
            floor_y = self._floor_to_y(floor)
            pg.draw.rect(screen, shaft_color, (self.x - 5, floor_y, self.width + 10, self.height), 1)

        # Draw lift cabin
        pg.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

        # Draw door indicator
        if self.door_open:
            door_color = (255, 255, 100)
            pg.draw.rect(screen, door_color, (self.x + 5, self.y + 5, self.width - 10, 5))

        # Draw lift name
        font = pg.font.Font(None, 36)
        text = font.render(self.name, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

        # Draw customer count
        if self.customers_inside:
            count_font = pg.font.Font(None, 24)
            count_text = count_font.render(f"{len(self.customers_inside)}", True, (255, 255, 255))
            screen.blit(count_text, (self.x + 5, self.y + self.height - 25))
