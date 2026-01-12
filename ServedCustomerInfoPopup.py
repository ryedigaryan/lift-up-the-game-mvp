import pygame as pg


class ServedCustomerInfoPopup:
    def __init__(self, customer):
        self.customer = customer
        self.width = 120
        self.height = 60
        self.font = pg.font.Font(None, 18)

    def draw(self, screen):
        # Don't draw if customer is in lift
        if self.customer.state == "in_lift":
            return

        # Calculate current penalty and waiting time
        current_time = pg.time.get_ticks() / 1000.0
        
        # Waiting time: time since request
        waiting_time = current_time - self.customer.request_time
        
        # Calculate current penalty using customer's method
        penalty = self.customer.calculate_penalty(current_time)

        # Position popup above customer
        popup_x = self.customer.x - self.width // 2 + self.customer.width // 2
        popup_y = self.customer.y - self.height - 5
        
        # Draw background using customer's color
        pg.draw.rect(screen, self.customer.color, (popup_x, popup_y, self.width, self.height))
        pg.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, self.width, self.height), 1)
        
        # Draw text
        # Line 1: Target Floor
        target_text = self.font.render(f"Target: {self.customer.target_floor}", True, (0, 0, 0))
        screen.blit(target_text, (popup_x + 5, popup_y + 5))
        
        # Line 2: Elapsed Time
        time_text = self.font.render(f"Time: {waiting_time:.1f}s", True, (0, 0, 0))
        screen.blit(time_text, (popup_x + 5, popup_y + 22))
        
        # Line 3: Penalty
        penalty_text = self.font.render(f"Penalty: {penalty:.2f}", True, (200, 0, 0))
        screen.blit(penalty_text, (popup_x + 5, popup_y + 39))
