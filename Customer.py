from typing import Tuple, Dict
import pygame as pg
import random
from FloorRequestPopup import FloorRequestPopup
from ServedCustomerInfoPopup import ServedCustomerInfoPopup
from DeliveredCustomerPopup import DeliveredCustomerPopup
from PenaltyAttributes import PenaltyAttributes


class Customer:
    def __init__(self, spawn_floor: int, spawn_x: int, floor_width: int, target_floor: int, color: Tuple[int, int, int], popup_offset_y: int, is_high_priority: bool):
        self.current_floor = spawn_floor
        self.target_floor = target_floor
        self.spawn_x = spawn_x
        self.x = spawn_x
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.width = 20
        self.height = 40
        self.state = "waiting_for_lift_selection"  # waiting_for_lift_selection, walking_to_lift, waiting_at_lift, in_lift, exiting_lift, delivered
        self.selected_lift = None
        self.speed = 120  # pixels per second
        self.show_popup = True
        self.target_spawn_x = None  # Will be set when exiting lift
        self.is_active = False  # Is this customer's popup currently active?
        
        # Wandering properties
        self.floor_width = floor_width
        self.wandering_speed = 30  # pixels per second
        self.wandering_direction = random.choice([-1, 1])
        
        self.color = color
        self.is_high_priority = is_high_priority
        
        # Determine penalty attributes based on priority
        if self.is_high_priority:
            self.penalty_attributes = PenaltyAttributes.variant_2()
        else:
            self.penalty_attributes = PenaltyAttributes.variant_1()

        # Popups
        self.popup = FloorRequestPopup(self, popup_offset_y)
        self.info_popup = ServedCustomerInfoPopup(self)
        self.delivered_popup = DeliveredCustomerPopup(self)

        # Penalty attributes
        self.request_time = pg.time.get_ticks() / 1000.0
        self.assignment_time = None
        self.delivery_time = None

    def set_y(self, y_position: int):
        self.y = y_position

    def select_lift(self, lift_name: str):
        """Player selects a lift for this customer"""
        self.selected_lift = lift_name
        self.state = "walking_to_lift"
        self.show_popup = False
        self.is_active = False
        self.assignment_time = pg.time.get_ticks() / 1000.0

    def calculate_penalty(self, current_time: float) -> float:
        """
        Calculate penalty for this customer up to the given current_time.
        This method can calculate running penalty before assignment, before delivery, and the final penalty.
        """
        X = self.request_time
        Y = self.assignment_time
        Z = self.delivery_time

        apc = self.penalty_attributes.apc
        dpc = self.penalty_attributes.dpc
        cipc = self.penalty_attributes.cipc

        if Y is None:  # Not assigned yet
            # Penalty is just the waiting part, with Y treated as current_time
            wait_penalty = (current_time - X) * apc
            return wait_penalty * cipc
        
        # Assigned, but maybe not delivered
        assignment_penalty = (Y - X) * apc
        
        delivery_end_time = Z if Z is not None else current_time
        delivery_penalty = (delivery_end_time - Y) * dpc
        
        return (assignment_penalty + delivery_penalty) * cipc

    def update(self, dt: float, lift_positions: Dict[str, int]):
        self.vx = 0
        if self.state == "waiting_for_lift_selection":
            # Wander slowly if not active (mouse not hovering over popup)
            if not self.is_active:
                self.vx = self.wandering_speed * self.wandering_direction
                
                # Bounce off edges (keeping some margin)
                margin = 100
                if self.x < margin:
                    self.x = margin
                    self.wandering_direction = 1
                elif self.x > self.floor_width - margin - self.width:
                    self.x = self.floor_width - margin - self.width
                    self.wandering_direction = -1

        elif self.state == "walking_to_lift" and self.selected_lift:
            # Walk towards the selected lift
            target_x = lift_positions[self.selected_lift]
            if abs(self.x - target_x) < 2: # Snap to position
                self.x = target_x
                self.state = "waiting_at_lift"
            else:
                self.vx = self.speed if self.x < target_x else -self.speed
                
        elif self.state == "exiting_lift":
            # Walk towards the target floor's spawn location
            target_x = self.target_spawn_x if self.target_spawn_x else self.spawn_x
            if abs(self.x - target_x) < 2:
                self.x = target_x
                self.state = "delivered"
            else:
                self.vx = self.speed if self.x < target_x else -self.speed
        self.x += self.vx * dt

    def enter_lift(self):
        """Customer enters the lift"""
        self.state = "in_lift"

    def exit_lift(self, floor: int, lift_x: int, target_spawn_x: int):
        """Customer exits the lift at target floor"""
        if floor == self.target_floor:
            self.state = "exiting_lift"
            self.current_floor = floor
            self.x = lift_x  # Start at lift position
            self.target_spawn_x = target_spawn_x  # Where to walk to
            self.delivery_time = pg.time.get_ticks() / 1000.0

    def draw(self, screen: pg.Surface, draw_popup: bool = False):
        """Draw the customer"""

        # Don't draw when in lift
        if self.state == "in_lift":
            return

        if draw_popup:
            # Draw the correct popup based on state
            if self.state == "delivered" or self.state == "exiting_lift":
                self.delivered_popup.draw(screen)
            elif self.show_popup:
                self.popup.draw(screen)
            else:
                self.info_popup.draw(screen)
        else:
            # Only draw customer body
            # Change color based on state
            if self.state == "delivered" or self.state == "exiting_lift":
                # Use a brighter green to match the delivered popup
                pg.draw.rect(screen, (144, 238, 144), (self.x, self.y, self.width, self.height))
            else:
                if self.is_high_priority:
                    # Draw triangle for high priority
                    points = [
                        (self.x + self.width // 2, self.y),
                        (self.x, self.y + self.height),
                        (self.x + self.width, self.y + self.height)
                    ]
                    pg.draw.polygon(screen, self.color, points)
                else:
                    # Draw rectangle for normal priority
                    pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def is_mouse_over_popup(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if mouse is over the popup"""
        return self.popup.is_mouse_over(mouse_pos)

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click on popup buttons"""
        return self.popup.handle_click(mouse_pos)
