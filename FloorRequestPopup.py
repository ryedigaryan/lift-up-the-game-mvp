import pygame as pg
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from Customer import Customer


class FloorRequestPopup:
    def __init__(self, customer: Customer, offset_y: int = 0):
        self.customer = customer
        self.popup_width = 180  # Increased width for new layout
        self.popup_height = 100
        self.button_width = 50
        self.button_height = 30
        self.offset_y = offset_y
        self.font = pg.font.Font(None, 18)
        self.button_font = pg.font.Font(None, 24)
        self.circle_font = pg.font.Font(None, 28)

    def get_popup_rect(self) -> Tuple[int, int, int, int]:
        """Get the popup rectangle"""
        popup_x = self.customer.x - self.popup_width // 2 + self.customer.width // 2
        popup_y = self.customer.y - self.popup_height - 5 - self.offset_y
        return popup_x, popup_y, self.popup_width, self.popup_height

    def is_mouse_over(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if mouse is over the popup"""
        if not self.customer.show_popup or self.customer.state != "waiting_for_lift_selection":
            return False

        popup_x, popup_y, popup_width, popup_height = self.get_popup_rect()
        mx, my = mouse_pos
        return popup_x <= mx <= popup_x + popup_width and popup_y <= my <= popup_y + popup_height

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse click on popup buttons"""
        if not self.customer.show_popup or self.customer.state != "waiting_for_lift_selection":
            return False

        popup_x, popup_y, popup_width, _ = self.get_popup_rect()
        
        # Corrected button coordinates to match the draw method
        button_a_x = popup_x + 15
        button_b_x = popup_x + popup_width - self.button_width - 15
        button_y = popup_y + 60

        mx, my = mouse_pos

        # Check Lift A button
        if button_a_x <= mx <= button_a_x + self.button_width and button_y <= my <= button_y + self.button_height:
            self.customer.select_lift("A")
            return True

        # Check Lift B button
        if button_b_x <= mx <= button_b_x + self.button_width and button_y <= my <= button_y + self.button_height:
            self.customer.select_lift("B")
            return True

        return False

    def draw(self, screen: pg.Surface):
        """Draw the popup"""
        if not self.customer.show_popup or self.customer.state != "waiting_for_lift_selection":
            return

        popup_x, popup_y, popup_width, popup_height = self.get_popup_rect()

        # --- Background ---
        pg.draw.rect(screen, self.customer.color, (popup_x, popup_y, popup_width, popup_height))
        pg.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, popup_width, popup_height), 2)

        # --- Circle with Target Floor ---
        circle_radius = 22
        circle_x = popup_x + circle_radius + 8
        circle_y = popup_y + 30 # Centered in the top part
        pg.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), circle_radius)
        pg.draw.circle(screen, (0, 0, 0), (circle_x, circle_y), circle_radius, 2)
        
        target_text_surf = self.circle_font.render(str(self.customer.target_floor), True, (0, 0, 0))
        target_text_rect = target_text_surf.get_rect(center=(circle_x, circle_y))
        screen.blit(target_text_surf, target_text_rect)

        # --- Text Info (to the right of the circle) ---
        text_x = popup_x + (2 * circle_radius) + 15
        
        # Draw semi-transparent background for text
        text_bg_rect = pg.Rect(text_x - 3, popup_y + 8, self.popup_width - (text_x - popup_x) - 5, 44)
        text_bg_surf = pg.Surface(text_bg_rect.size, pg.SRCALPHA)
        text_bg_surf.fill((255, 255, 255, 128))
        screen.blit(text_bg_surf, text_bg_rect.topleft)
        
        current_time = pg.time.get_ticks() / 1000.0
        waiting_time = current_time - self.customer.request_time
        penalty = self.customer.calculate_penalty(current_time)

        # Wait Time
        wait_text = self.font.render(f"Wait: {waiting_time:.1f}s", True, (0, 0, 0))
        screen.blit(wait_text, (text_x, popup_y + 10))
        
        # Penalty
        penalty_text = self.font.render(f"Penalty: {int(penalty)}", True, (200, 0, 0))
        screen.blit(penalty_text, (text_x, popup_y + 32))

        # --- Buttons ---
        button_a_x = popup_x + 15
        button_b_x = popup_x + popup_width - self.button_width - 15
        button_y = popup_y + 60

        # Lift A button
        pg.draw.rect(screen, (100, 200, 100), (button_a_x, button_y, self.button_width, self.button_height))
        pg.draw.rect(screen, (0, 0, 0), (button_a_x, button_y, self.button_width, self.button_height), 2)
        text_a = self.button_font.render("A", True, (0, 0, 0))
        screen.blit(text_a, (button_a_x + 18, button_y + 5))

        # Lift B button
        pg.draw.rect(screen, (200, 100, 100), (button_b_x, button_y, self.button_width, self.button_height))
        pg.draw.rect(screen, (0, 0, 0), (button_b_x, button_y, self.button_width, self.button_height), 2)
        text_b = self.button_font.render("B", True, (0, 0, 0))
        screen.blit(text_b, (button_b_x + 18, button_y + 5))
