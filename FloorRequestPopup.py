import pygame as pg


class FloorRequestPopup:
    def __init__(self, customer, offset_y=0):
        self.customer = customer
        self.popup_width = 150
        self.popup_height = 80
        self.button_width = 50
        self.button_height = 30
        self.offset_y = offset_y

    def get_popup_rect(self):
        """Get the popup rectangle"""
        popup_x = self.customer.x - self.popup_width // 2 + self.customer.width // 2
        # Apply random offset to Y position
        # Shifted down by reducing the base subtraction (from -10 to -5)
        popup_y = self.customer.y - self.popup_height - 5 - self.offset_y
        return popup_x, popup_y, self.popup_width, self.popup_height

    def is_mouse_over(self, mouse_pos):
        """Check if mouse is over the popup"""
        if not self.customer.show_popup or self.customer.state != "waiting_for_lift_selection":
            return False

        popup_x, popup_y, popup_width, popup_height = self.get_popup_rect()
        mx, my = mouse_pos
        return popup_x <= mx <= popup_x + popup_width and popup_y <= my <= popup_y + popup_height

    def handle_click(self, mouse_pos):
        """Handle mouse click on popup buttons"""
        if not self.customer.show_popup or self.customer.state != "waiting_for_lift_selection":
            return False

        popup_x, popup_y, _, _ = self.get_popup_rect()
        button_a_x = popup_x + 15
        button_b_x = popup_x + 85
        button_y = popup_y + 40

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

    def draw(self, screen):
        """Draw the popup"""
        if not self.customer.show_popup or self.customer.state != "waiting_for_lift_selection":
            return

        popup_x, popup_y, popup_width, popup_height = self.get_popup_rect()

        # Draw popup background using customer's color
        pg.draw.rect(screen, self.customer.color, (popup_x, popup_y, popup_width, popup_height))
        pg.draw.rect(screen, (0, 0, 0), (popup_x, popup_y, popup_width, popup_height), 2)

        # Draw text
        font = pg.font.Font(None, 24)
        text = font.render(f"Floor {self.customer.target_floor}", True, (0, 0, 0))
        screen.blit(text, (popup_x + 10, popup_y + 10))

        # Draw lift selection buttons
        button_a_x = popup_x + 15
        button_b_x = popup_x + 85
        button_y = popup_y + 40

        # Lift A button
        pg.draw.rect(screen, (100, 200, 100), (button_a_x, button_y, self.button_width, self.button_height))
        pg.draw.rect(screen, (0, 0, 0), (button_a_x, button_y, self.button_width, self.button_height), 2)
        text_a = font.render("A", True, (0, 0, 0))
        screen.blit(text_a, (button_a_x + 18, button_y + 5))

        # Lift B button
        pg.draw.rect(screen, (200, 100, 100), (button_b_x, button_y, self.button_width, self.button_height))
        pg.draw.rect(screen, (0, 0, 0), (button_b_x, button_y, self.button_width, self.button_height), 2)
        text_b = font.render("B", True, (0, 0, 0))
        screen.blit(text_b, (button_b_x + 18, button_y + 5))
