from __future__ import annotations
import pygame as pg
import time
from typing import TYPE_CHECKING, List
from post_level.PostLevelCompleteAction import PostLevelCompleteAction
from GameHistoryPersistence import GameHistoryPersistence
from RawGameHistoryEntry import RawGameHistoryEntry

if TYPE_CHECKING:
    from Level import Level
    from LiftUpGame import LiftUpGame
    from post_level.LoadNextLevelAction import LoadNextLevelAction


class LevelTransitionAction(PostLevelCompleteAction):
    def __init__(self, game: LiftUpGame, level_num: int, next_level_action: LoadNextLevelAction):
        self.game = game
        self.level_num = level_num
        self.next_level_action = next_level_action
        self.persistence = GameHistoryPersistence("data/output")

    def execute(self, level: Level):
        screen = pg.display.get_surface()
        clock = pg.time.Clock()
        final_penalty = level.status_bar.total_penalty

        # --- Data Processing ---
        level_name = f"level_{self.level_num}"
        level_history = [entry for entry in self.persistence.read_all() if entry.level == level_name]
        level_history.sort(key=lambda x: x.timestamp_epoch_seconds, reverse=True)

        # --- UI Setup ---
        title_font = pg.font.Font(None, 74)
        score_font = pg.font.Font(None, 60)
        header_font = pg.font.Font(None, 50)
        row_font = pg.font.Font(None, 32)
        button_font = pg.font.Font(None, 40)

        WHITE = (255, 255, 255)
        GREY = (150, 150, 150)
        GREEN = (100, 200, 100)
        BLUE = (100, 100, 200)
        RED = (200, 100, 100)
        GOLD = (255, 215, 0)
        BACKGROUND = (30, 30, 30)

        # --- Button Rects ---
        button_width, button_height = 200, 60
        total_width = button_width * 3 + 40
        start_x = (screen.get_width() - total_width) / 2
        
        next_level_button_rect = pg.Rect(start_x, screen.get_height() - 100, button_width, button_height)
        replay_button_rect = pg.Rect(start_x + button_width + 20, screen.get_height() - 100, button_width, button_height)
        exit_button_rect = pg.Rect(start_x + (button_width + 20) * 2, screen.get_height() - 100, button_width, button_height)

        running = True
        while running:
            mouse_pos = pg.mouse.get_pos()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.current_level = None # Signal game to exit
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if next_level_button_rect.collidepoint(mouse_pos):
                        self.next_level_action.execute(level)
                        running = False
                    elif replay_button_rect.collidepoint(mouse_pos):
                        self.game.load_and_set_level(self.level_num)
                        running = False
                    elif exit_button_rect.collidepoint(mouse_pos):
                        self.game.current_level = None # Signal game to exit
                        running = False

            screen.fill(BACKGROUND)

            # --- Draw UI Elements ---
            # Title
            title_surf = title_font.render(f"Level {self.level_num} Complete!", True, GOLD)
            screen.blit(title_surf, title_surf.get_rect(center=(screen.get_width() / 2, 80)))

            # Final Score
            score_text_surf = row_font.render("Your Penalty:", True, WHITE)
            screen.blit(score_text_surf, score_text_surf.get_rect(center=(screen.get_width() / 2, 160)))
            score_val_surf = score_font.render(f"{final_penalty:.2f}", True, GOLD)
            screen.blit(score_val_surf, score_val_surf.get_rect(center=(screen.get_width() / 2, 210)))

            # Level History
            y_offset = 300
            history_header_surf = header_font.render("Level History", True, WHITE)
            screen.blit(history_header_surf, history_header_surf.get_rect(center=(screen.get_width() / 2, y_offset)))
            y_offset += 50
            pg.draw.line(screen, GOLD, (100, y_offset), (screen.get_width() - 100, y_offset), 1)
            y_offset += 30

            for entry in level_history[:5]: # Show top 5 for this level
                date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(entry.timestamp_epoch_seconds))
                penalty_str = f"{entry.penalty:.2f}"
                
                date_surf = row_font.render(date_str, True, GREY)
                penalty_surf = row_font.render(penalty_str, True, WHITE)
                
                screen.blit(date_surf, date_surf.get_rect(center=(screen.get_width() / 2 - 100, y_offset)))
                screen.blit(penalty_surf, penalty_surf.get_rect(center=(screen.get_width() / 2 + 150, y_offset)))
                y_offset += 40

            # Buttons
            pg.draw.rect(screen, GREEN, next_level_button_rect, border_radius=10)
            next_text = button_font.render("Next Level", True, BACKGROUND)
            screen.blit(next_text, next_text.get_rect(center=next_level_button_rect.center))

            pg.draw.rect(screen, BLUE, replay_button_rect, border_radius=10)
            replay_text = button_font.render("Replay", True, BACKGROUND)
            screen.blit(replay_text, replay_text.get_rect(center=replay_button_rect.center))

            pg.draw.rect(screen, RED, exit_button_rect, border_radius=10)
            exit_text = button_font.render("Exit", True, BACKGROUND)
            screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))

            pg.display.flip()
            clock.tick(60)
