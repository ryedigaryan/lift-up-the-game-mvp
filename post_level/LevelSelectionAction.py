from __future__ import annotations
import pygame as pg
from typing import TYPE_CHECKING, Callable
from post_level.PostLevelCompleteAction import PostLevelCompleteAction

if TYPE_CHECKING:
    from Level import Level
    from LevelsLoader import LevelsLoader


class LevelSelectionAction(PostLevelCompleteAction):
    def __init__(self, levels_loader: LevelsLoader, level_runner_factory: Callable[[int], PostLevelCompleteAction]):
        self.levels_loader = levels_loader
        self.level_runner_factory = level_runner_factory

    def execute(self, level: Level):
        screen = pg.display.get_surface()
        width, height = screen.get_size()

        # --- Find available levels ---
        available_levels = []
        level_num = 1
        while self.levels_loader.level_exists(level_num):
            available_levels.append(level_num)
            level_num += 1

        # --- UI Setup ---
        title_font = pg.font.Font(None, 74)
        button_font = pg.font.Font(None, 50)
        
        WHITE = (255, 255, 255)
        GOLD = (255, 215, 0)
        BLUE = (100, 100, 200)
        BACKGROUND = (30, 30, 30)

        # --- Button Setup ---
        buttons = []
        button_width, button_height = 120, 80
        cols = 5
        gap = 20
        start_x = (width - (cols * button_width + (cols - 1) * gap)) / 2
        start_y = 200

        for i, num in enumerate(available_levels):
            row = i // cols
            col = i % cols
            x = start_x + col * (button_width + gap)
            y = start_y + row * (button_height + gap)
            rect = pg.Rect(x, y, button_width, button_height)
            buttons.append((rect, f"Level {num}", BLUE, self.level_runner_factory(num)))

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # In a real game, you might want an ExitAction here, but for now, we just exit the loop
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    for rect, _, _, action in buttons:
                        if rect.collidepoint(event.pos):
                            action.execute(level)
                            running = False
                            break
            
            screen.fill(BACKGROUND)
            title_surf = title_font.render("Select a Level", True, GOLD)
            screen.blit(title_surf, title_surf.get_rect(center=(width / 2, 100)))

            for rect, text, color, _ in buttons:
                pg.draw.rect(screen, color, rect, border_radius=10)
                text_surf = button_font.render(text, True, WHITE)
                screen.blit(text_surf, text_surf.get_rect(center=rect.center))

            pg.display.flip()
