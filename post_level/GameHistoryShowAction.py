from __future__ import annotations
import pygame as pg
import time
from typing import TYPE_CHECKING, Dict
from post_level.PostLevelCompleteAction import PostLevelCompleteAction
from GameHistoryPersistence import GameHistoryPersistence
from RawGameHistoryEntry import RawGameHistoryEntry

if TYPE_CHECKING:
    from Level import Level


class GameHistoryShowAction(PostLevelCompleteAction):
    def __init__(self, persistence: GameHistoryPersistence):
        self.persistence = persistence

    def execute(self, level: Level):
        """
        Takes over the screen to display a summary of the player's best performance for each level.
        """
        screen = pg.display.get_surface()
        clock = pg.time.Clock()

        # --- Data Processing ---
        all_history = self.persistence.read_all()
        best_scores: Dict[str, RawGameHistoryEntry] = {}

        for entry in all_history:
            if entry.level not in best_scores or entry.penalty < best_scores[entry.level].penalty:
                best_scores[entry.level] = entry
        
        sorted_levels = sorted(best_scores.keys(), key=lambda x: int(x.split('_')[-1]))
        recent_runs = sorted(all_history, key=lambda x: x.timestamp_epoch_seconds, reverse=True)[:10]

        # --- UI Setup ---
        title_font = pg.font.Font(None, 74)
        header_font = pg.font.Font(None, 50)
        row_font = pg.font.Font(None, 36)
        small_row_font = pg.font.Font(None, 28)
        prompt_font = pg.font.Font(None, 28)

        WHITE = (255, 255, 255)
        GREY = (150, 150, 150)
        GOLD = (255, 215, 0)
        BACKGROUND = (30, 30, 30)

        # --- Main Loop for History Screen ---
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key in [pg.K_ESCAPE, pg.K_RETURN]):
                    running = False

            screen.fill(BACKGROUND)

            # 1. Draw Title
            title_surf = title_font.render("Your Performance", True, GOLD)
            title_rect = title_surf.get_rect(center=(screen.get_width() / 2, 60))
            screen.blit(title_surf, title_rect)

            # 2. Draw Best Scores Table
            y_offset = 150
            col_level_x = 150
            col_penalty_x = 400
            col_date_x = 650

            header_level = header_font.render("Level", True, WHITE)
            header_penalty = header_font.render("Best Penalty", True, WHITE)
            header_date = header_font.render("Date", True, WHITE)

            screen.blit(header_level, header_level.get_rect(center=(col_level_x, y_offset)))
            screen.blit(header_penalty, header_penalty.get_rect(center=(col_penalty_x, y_offset)))
            screen.blit(header_date, header_date.get_rect(center=(col_date_x, y_offset)))
            
            pg.draw.line(screen, GOLD, (50, y_offset + 30), (screen.get_width() - 50, y_offset + 30), 2)

            y_offset += 60
            for level_name in sorted_levels:
                entry = best_scores[level_name]
                level_surf = row_font.render(level_name.replace('_', ' ').title(), True, WHITE)
                penalty_surf = row_font.render(f"{entry.penalty:.2f}", True, WHITE)
                date_str = time.strftime('%Y-%m-%d', time.localtime(entry.timestamp_epoch_seconds))
                date_surf = row_font.render(date_str, True, GREY)

                screen.blit(level_surf, level_surf.get_rect(center=(col_level_x, y_offset)))
                screen.blit(penalty_surf, penalty_surf.get_rect(center=(col_penalty_x, y_offset)))
                screen.blit(date_surf, date_surf.get_rect(center=(col_date_x, y_offset)))
                y_offset += 40

            # 3. Draw Full History Section
            y_offset += 40
            history_title_surf = header_font.render("Recent Runs", True, GOLD)
            screen.blit(history_title_surf, history_title_surf.get_rect(center=(screen.get_width() / 2, y_offset)))
            y_offset += 50
            
            pg.draw.line(screen, GOLD, (50, y_offset - 10), (screen.get_width() - 50, y_offset - 10), 2)
            
            y_offset += 20  # Added padding

            for entry in recent_runs:
                level_surf = small_row_font.render(entry.level.replace('_', ' ').title(), True, WHITE)
                penalty_surf = small_row_font.render(f"{entry.penalty:.2f}", True, WHITE)
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(entry.timestamp_epoch_seconds))
                date_surf = small_row_font.render(date_str, True, GREY)

                screen.blit(level_surf, level_surf.get_rect(center=(col_level_x, y_offset)))
                screen.blit(penalty_surf, penalty_surf.get_rect(center=(col_penalty_x, y_offset)))
                screen.blit(date_surf, date_surf.get_rect(center=(col_date_x, y_offset)))
                y_offset += 30

            # 4. Draw Exit Prompt
            prompt_surf = prompt_font.render("Press ENTER or ESC to exit", True, GREY)
            prompt_rect = prompt_surf.get_rect(center=(screen.get_width() / 2, screen.get_height() - 40))
            screen.blit(prompt_surf, prompt_rect)

            pg.display.flip()
            clock.tick(60)
