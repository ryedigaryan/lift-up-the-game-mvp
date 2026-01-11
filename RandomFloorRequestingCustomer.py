import pygame as pg
import random
from FloorRequestPopup import FloorRequestPopup


class RandomFloorRequestingCustomer:
    def __init__(self, spawn_floor, spawn_x, total_floors, floor_width):
        self.current_floor = spawn_floor
        self.target_floor = self._request_random_floor(spawn_floor, total_floors)
        self.spawn_x = spawn_x
        self.x = spawn_x
        self.y = 0  # Will be set by floor
        self.width = 20
        self.height = 40
        self.state = "waiting_for_lift_selection"  # waiting_for_lift_selection, walking_to_lift, waiting_at_lift, in_lift, exiting_lift, delivered
        self.selected_lift = None
        self.speed = 2
        self.show_popup = True
        self.target_spawn_x = None  # Will be set when exiting lift
        
        # Wandering properties
        self.floor_width = floor_width
        self.wandering_speed = 0.5
        self.wandering_direction = random.choice([-1, 1])
        
        # Random color
        self.color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        
        # Random popup offset (between 0 and 30 pixels higher)
        offset_y = random.randint(0, 30)
        self.popup = FloorRequestPopup(self, offset_y)

    def _request_random_floor(self, current_floor, total_floors):
        """Request a random floor different from current floor"""
        available_floors = [f for f in range(total_floors) if f != current_floor]
        return random.choice(available_floors)

    def select_lift(self, lift_name):
        """Player selects a lift for this customer"""
        self.selected_lift = lift_name
        self.state = "walking_to_lift"
        self.show_popup = False

    def update(self, lift_positions):
        """Update customer state and position"""
        if self.state == "waiting_for_lift_selection":
            # Wander slowly if mouse is not over popup
            mouse_pos = pg.mouse.get_pos()
            if not self.is_mouse_over_popup(mouse_pos):
                self.x += self.wandering_speed * self.wandering_direction
                
                # Bounce off edges (keeping some margin)
                margin = 50
                if self.x < margin:
                    self.x = margin
                    self.wandering_direction = 1
                elif self.x > self.floor_width - margin - self.width:
                    self.x = self.floor_width - margin - self.width
                    self.wandering_direction = -1

        elif self.state == "walking_to_lift" and self.selected_lift:
            # Walk towards the selected lift
            target_x = lift_positions[self.selected_lift]
            if abs(self.x - target_x) < self.speed:
                self.x = target_x
                self.state = "waiting_at_lift"
            elif self.x < target_x:
                self.x += self.speed
            else:
                self.x -= self.speed
        elif self.state == "exiting_lift":
            # Walk towards the target floor's spawn location
            target_x = self.target_spawn_x if self.target_spawn_x else self.spawn_x
            if abs(self.x - target_x) < self.speed:
                self.x = target_x
                self.state = "delivered"
            elif self.x < target_x:
                self.x += self.speed
            else:
                self.x -= self.speed

    def enter_lift(self):
        """Customer enters the lift"""
        self.state = "in_lift"

    def exit_lift(self, floor, lift_x, target_spawn_x):
        """Customer exits the lift at target floor"""
        if floor == self.target_floor:
            self.state = "exiting_lift"
            self.current_floor = floor
            self.x = lift_x  # Start at lift position
            self.target_spawn_x = target_spawn_x  # Where to walk to

    def draw(self, screen, y_position, draw_popup=False):
        """Draw the customer"""
        self.y = y_position

        # Don't draw when in lift
        if self.state == "in_lift":
            return

        if draw_popup:
            # Only draw popup
            self.popup.draw(screen)
        else:
            # Only draw customer body
            # Change color based on state
            if self.state == "exiting_lift":
                # Flash green or just use their color but brighter?
                # Let's keep the "delivered" feedback distinct
                pg.draw.rect(screen, (50, 255, 50), (self.x, self.y, self.width, self.height))
            else:
                pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def is_mouse_over_popup(self, mouse_pos):
        """Check if mouse is over the popup"""
        return self.popup.is_mouse_over(mouse_pos)

    def handle_click(self, mouse_pos):
        """Handle mouse click on popup buttons"""
        return self.popup.handle_click(mouse_pos)
