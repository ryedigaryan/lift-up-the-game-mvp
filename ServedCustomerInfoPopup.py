import pygame as pg


class ServedCustomerInfoPopup:
    def __init__(self, customer):
        self.customer = customer
        self.width = 150  # Increased width for new layout
        self.height = 60
        self.font = pg.font.Font(None, 18)
        self.circle_font = pg.font.Font(None, 28)

    def draw(self, screen):
        # Don't draw if customer is in lift
        if self.customer.state == "in_lift":
            return

        # Calculate current penalty and waiting time
        current_time = pg.time.get_ticks() / 1000.0
        waiting_time = current_time - self.customer.request_time
        penalty = self.customer.calculate_penalty(current_time)

        # --- Position and Background ---
        popup_x = self.customer.x - self.width // 2 + self.customer.width // 2
        popup_y = self.customer.y - self.height - 5
        
        pg.draw.rect(screen, self.customer.color, (popup_x, popup_y, self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, self.width, self.height), 1)
        
        # --- Draw Circle with Target Floor ---
        circle_radius = 22
        circle_x = popup_x + circle_radius + 8
        circle_y = popup_y + self.height // 2
        pg.draw.circle(screen, (255, 255, 255), (circle_x, circle_y), circle_radius)
        pg.draw.circle(screen, (0, 0, 0), (circle_x, circle_y), circle_radius, 2)
        
        target_text_surf = self.circle_font.render(str(self.customer.target_floor), True, (0, 0, 0))
        target_text_rect = target_text_surf.get_rect(center=(circle_x, circle_y))
        screen.blit(target_text_surf, target_text_rect)

        # --- Draw Text Info (to the right of the circle) ---
        text_x = popup_x + (2 * circle_radius) + 15
        
        # Draw semi-transparent background for text
        text_bg_rect = pg.Rect(text_x - 3, popup_y + 8, self.width - (text_x - popup_x) - 5, 44)
        text_bg_surf = pg.Surface(text_bg_rect.size, pg.SRCALPHA)
        text_bg_surf.fill((255, 255, 255, 128))
        screen.blit(text_bg_surf, text_bg_rect.topleft)
        
        # Wait Time
        wait_text = self.font.render(f"Wait: {waiting_time:.1f}s", True, (0, 0, 0))
        screen.blit(wait_text, (text_x, popup_y + 10))
        
        # Penalty
        penalty_text = self.font.render(f"Penalty: {int(penalty)}", True, (200, 0, 0))
        screen.blit(penalty_text, (text_x, popup_y + 32))
