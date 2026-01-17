from typing import Tuple, Dict
import pygame as pg
import random
from FloorRequestPopup import FloorRequestPopup
from ServedCustomerInfoPopup import ServedCustomerInfoPopup
from DeliveredCustomerPopup import DeliveredCustomerPopup
from PenaltyAttributes import PenaltyAttributes


class Customer:
    def __init__(self, spawn_floor: int, spawn_x: int, floor_width: int, target_floor: int, color: Tuple[int, int, int], popup_offset_y: int, is_high_priority: bool, request_time: float):
        self.current_floor = spawn_floor
        self.target_floor = target_floor
        self.spawn_x = spawn_x
        self.x = spawn_x
        self.y = 0
        self.width = 20
        self.height = 40
        self.state = "waiting_for_lift_selection"
        self.selected_lift = None
        self.speed = 2
        self.show_popup = True
        self.target_spawn_x = None
        self.is_active = False
        
        self.floor_width = floor_width
        self.wandering_speed = 0.5
        self.wandering_direction = random.choice([-1, 1])
        
        self.color = color
        self.is_high_priority = is_high_priority
        
        if self.is_high_priority:
            self.penalty_attributes = PenaltyAttributes.variant_2()
        else:
            self.penalty_attributes = PenaltyAttributes.variant_1()

        self.popup = FloorRequestPopup(self, popup_offset_y)
        self.info_popup = ServedCustomerInfoPopup(self)
        self.delivered_popup = DeliveredCustomerPopup(self)

        self.request_time = request_time
        self.assignment_time = None
        self.delivery_time = None

    def set_y(self, y_position: int):
        self.y = y_position

    def select_lift(self, lift_name: str, current_time: float):
        self.selected_lift = lift_name
        self.state = "walking_to_lift"
        self.show_popup = False
        self.is_active = False
        self.assignment_time = current_time

    def calculate_penalty(self, current_time: float) -> float:
        X = self.request_time
        Y = self.assignment_time
        Z = self.delivery_time
        apc, dpc, cipc = self.penalty_attributes.apc, self.penalty_attributes.dpc, self.penalty_attributes.cipc

        if Y is None:
            return (current_time - X) * apc * cipc
        
        assignment_penalty = (Y - X) * apc
        delivery_end_time = Z if Z is not None else current_time
        delivery_penalty = (delivery_end_time - Y) * dpc
        
        return (assignment_penalty + delivery_penalty) * cipc

    def update(self, lift_positions: Dict[str, int]):
        if self.state == "waiting_for_lift_selection":
            if not self.is_active:
                self.x += self.wandering_speed * self.wandering_direction
                
                margin = 100
                if self.x < margin:
                    self.x = margin
                    self.wandering_direction = 1
                elif self.x > self.floor_width - margin - self.width:
                    self.x = self.floor_width - margin - self.width
                    self.wandering_direction = -1

        elif self.state == "walking_to_lift" and self.selected_lift:
            target_x = lift_positions[self.selected_lift]
            if abs(self.x - target_x) < self.speed:
                self.x = target_x
                self.state = "waiting_at_lift"
            elif self.x < target_x:
                self.x += self.speed
            else:
                self.x -= self.speed
                
        elif self.state == "exiting_lift":
            target_x = self.target_spawn_x if self.target_spawn_x else self.spawn_x
            if abs(self.x - target_x) < self.speed:
                self.x = target_x
                self.state = "delivered"
            elif self.x < target_x:
                self.x += self.speed
            else:
                self.x -= self.speed

    def enter_lift(self):
        self.state = "in_lift"

    def exit_lift(self, floor: int, lift_x: int, target_spawn_x: int, current_time: float):
        if floor == self.target_floor:
            self.state = "exiting_lift"
            self.current_floor = floor
            self.x = lift_x
            self.target_spawn_x = target_spawn_x
            self.delivery_time = current_time

    def draw(self, screen: pg.Surface, draw_popup: bool = False):
        if self.state == "in_lift":
            return

        if draw_popup:
            if self.state in ["delivered", "exiting_lift"]:
                self.delivered_popup.draw(screen)
            elif self.show_popup:
                self.popup.draw(screen)
            else:
                self.info_popup.draw(screen)
        else:
            color = (144, 238, 144) if self.state in ["delivered", "exiting_lift"] else self.color
            if self.is_high_priority and self.state not in ["delivered", "exiting_lift"]:
                points = [(self.x + self.width // 2, self.y), (self.x, self.y + self.height), (self.x + self.width, self.y + self.height)]
                pg.draw.polygon(screen, color, points)
            else:
                pg.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

    def is_mouse_over_popup(self, mouse_pos: Tuple[int, int]) -> bool:
        return self.popup.is_mouse_over(mouse_pos)

    def handle_click(self, mouse_pos: Tuple[int, int], current_time: float) -> bool:
        return self.popup.handle_click(mouse_pos, current_time)
