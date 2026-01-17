import pygame as pg
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Customer import Customer


class DeliveredCustomerPopup:
    def __init__(self, customer: Customer):
        self.customer = customer
        self.width = 120
        self.height = 45
        self.font = pg.font.Font(None, 18)
        self.background_color = (144, 238, 144)  # Brighter green (lightgreen)

    def draw(self, screen: pg.Surface):
        # This popup is only for the final state, so calculations are based on set times
        if self.customer.delivery_time is None:
            return

        final_wait_time = self.customer.delivery_time - self.customer.request_time
        final_penalty = self.customer.calculate_penalty(self.customer.delivery_time)

        # --- Position and Background ---
        popup_x = self.customer.x - self.width // 2 + self.customer.width // 2
        popup_y = self.customer.y - self.height - 5
        
        pg.draw.rect(screen, self.background_color, (popup_x, popup_y, self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, self.width, self.height), 1)

        # --- Draw Text Info ---
        text_x = popup_x + 5
        
        # Wait Time
        wait_text = self.font.render(f"Final Wait: {final_wait_time:.1f}s", True, (0, 0, 0))
        screen.blit(wait_text, (text_x, popup_y + 5))
        
        # Penalty
        penalty_text = self.font.render(f"Final Penalty: {int(final_penalty)}", True, (200, 0, 0))
        screen.blit(penalty_text, (text_x, popup_y + 22))
