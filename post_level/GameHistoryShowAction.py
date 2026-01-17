from __future__ import annotations
import pygame as pg
import time
from typing import TYPE_CHECKING, Dict
from post_level.PostLevelCompleteAction import PostLevelCompleteAction
from GameHistoryPersistence import GameHistoryPersistence
from RawGameHistoryEntry import RawGameHistoryEntry

if TYPE_CHECKING:
    from Level import Level
    from LiftUpGame import LiftUpGame
    from post_level.ExitAction import ExitAction


class GameHistoryShowAction(PostLevelCompleteAction):
    def __init__(self,
                 game: LiftUpGame,
                 persistence: GameHistoryPersistence,
                 level_select_action: PostLevelCompleteAction,
                 exit_action: ExitAction):
        self.game = game
        self.persistence = persistence
        self.level_select_action = level_select_action
        self.exit_action = exit_action

    def execute(self, level: Level):
        screen = pg.display.get_surface()
        width, height = screen.get_size()

        # --- Surface Setup ---
        button_panel_height = 120
        history_panel_height = height - button_panel_height
        history_surface = pg.Surface((width, history_panel_height))
        button_surface = pg.Surface((width, button_panel_height))

        # --- Data Processing ---
        all_history = self.persistence.read_all()
        best_scores: Dict[str, RawGameHistoryEntry] = {}
        for entry in all_history:
            if entry.level not in best_scores or entry.penalty < best_scores[entry.level].penalty:
                best_scores[entry.level] = entry
        sorted_levels = sorted(best_scores.keys(), key=lambda x: int(x.split('_')[-1]))
        recent_runs = sorted(all_history, key=lambda x: x.timestamp_epoch_seconds, reverse=True)[:10]

        # --- UI Setup ---
        title_font, header_font, row_font, small_row_font, button_font = pg.font.Font(None, 74), pg.font.Font(None, 50), pg.font.Font(None, 36), pg.font.Font(None, 28), pg.font.Font(None, 32)
        WHITE, GREY, RED, PURPLE, GOLD, BACKGROUND, PANEL_BG = (255, 255, 255), (150, 150, 150), (200, 100, 100), (170, 100, 200), (255, 215, 0), (30, 30, 30), (40, 40, 40)

        # --- Button Setup ---
        buttons = [("Level Select", PURPLE, self.level_select_action), ("Exit", RED, self.exit_action)]
        button_width, button_height = 180, 60
        total_width = len(buttons) * button_width + (len(buttons) - 1) * 40
        start_x = (width - total_width) / 2
        button_rects = [(pg.Rect(start_x + i * (button_width + 40), (button_panel_height - button_height) / 2, button_width, button_height), text, color, action) for i, (text, color, action) in enumerate(buttons)]

        # --- Pre-render History Surface ---
        history_surface.fill(BACKGROUND)
        title_surf = title_font.render("Your Performance", True, GOLD)
        history_surface.blit(title_surf, title_surf.get_rect(center=(width / 2, 60)))
        
        y_offset, col_level_x, col_penalty_x, col_date_x = 150, 150, 400, 650
        history_surface.blit(header_font.render("Level", True, WHITE), header_font.render("Level", True, WHITE).get_rect(center=(col_level_x, y_offset)))
        history_surface.blit(header_font.render("Best Penalty", True, WHITE), header_font.render("Best Penalty", True, WHITE).get_rect(center=(col_penalty_x, y_offset)))
        history_surface.blit(header_font.render("Date", True, WHITE), header_font.render("Date", True, WHITE).get_rect(center=(col_date_x, y_offset)))
        pg.draw.line(history_surface, GOLD, (50, y_offset + 30), (width - 50, y_offset + 30), 2)
        y_offset += 60
        for level_name in sorted_levels:
            entry = best_scores[level_name]
            history_surface.blit(row_font.render(level_name.replace('_', ' ').title(), True, WHITE), row_font.render(level_name.replace('_', ' ').title(), True, WHITE).get_rect(center=(col_level_x, y_offset)))
            history_surface.blit(row_font.render(f"{entry.penalty:.2f}", True, WHITE), row_font.render(f"{entry.penalty:.2f}", True, WHITE).get_rect(center=(col_penalty_x, y_offset)))
            history_surface.blit(row_font.render(time.strftime('%Y-%m-%d', time.localtime(entry.timestamp_epoch_seconds)), True, GREY), row_font.render(time.strftime('%Y-%m-%d', time.localtime(entry.timestamp_epoch_seconds)), True, GREY).get_rect(center=(col_date_x, y_offset)))
            y_offset += 40
        
        y_offset += 40
        history_surface.blit(header_font.render("Recent Runs", True, GOLD), header_font.render("Recent Runs", True, GOLD).get_rect(center=(width / 2, y_offset)))
        y_offset += 50
        pg.draw.line(history_surface, GOLD, (50, y_offset - 10), (width - 50, y_offset - 10), 2)
        y_offset += 20
        for entry in recent_runs:
            history_surface.blit(small_row_font.render(entry.level.replace('_', ' ').title(), True, WHITE), small_row_font.render(entry.level.replace('_', ' ').title(), True, WHITE).get_rect(center=(col_level_x, y_offset)))
            history_surface.blit(small_row_font.render(f"{entry.penalty:.2f}", True, WHITE), small_row_font.render(f"{entry.penalty:.2f}", True, WHITE).get_rect(center=(col_penalty_x, y_offset)))
            history_surface.blit(small_row_font.render(time.strftime('%Y-%m-%d %H:%M', time.localtime(entry.timestamp_epoch_seconds)), True, GREY), small_row_font.render(time.strftime('%Y-%m-%d %H:%M', time.localtime(entry.timestamp_epoch_seconds)), True, GREY).get_rect(center=(col_date_x, y_offset)))
            y_offset += 30

        # --- Main Loop ---
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    # Adjust mouse_pos for button surface
                    mouse_y_on_button_surface = mouse_pos[1] - history_panel_height
                    for rect, _, _, action in button_rects:
                        if rect.collidepoint((mouse_pos[0], mouse_y_on_button_surface)):
                            action.execute(level)
                            running = False
                            break
            
            button_surface.fill(PANEL_BG)
            for rect, text, color, _ in button_rects:
                pg.draw.rect(button_surface, color, rect, border_radius=10)
                text_surf = button_font.render(text, True, BACKGROUND if color != GREY else WHITE)
                button_surface.blit(text_surf, text_surf.get_rect(center=rect.center))

            screen.blit(history_surface, (0, 0))
            screen.blit(button_surface, (0, history_panel_height))
            pg.display.flip()
