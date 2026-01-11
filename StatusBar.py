import pygame as pg


class StatusBar:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.surface = pg.Surface((width, height))
        self.total_penalty = 0.0
        self.font = pg.font.Font(None, 36)

    def add_penalty(self, penalty):
        self.total_penalty += penalty

    def draw(self, screen):
        self.surface.fill((50, 50, 50))  # Dark gray background
        
        # Draw penalty text
        text = self.font.render(f"Total Penalty: {int(self.total_penalty)}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.surface.blit(text, text_rect)
        
        # Blit status bar surface onto main screen
        screen.blit(self.surface, (self.x, self.y))
