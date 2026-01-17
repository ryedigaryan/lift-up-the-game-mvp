from __future__ import annotations
import pygame as pg
import time
from typing import TYPE_CHECKING, Optional
from post_level.PostLevelCompleteAction import PostLevelCompleteAction
from GameHistoryPersistence import GameHistoryPersistence

if TYPE_CHECKING:
    from Level import Level
    from LiftUpGame import LiftUpGame


class LevelTransitionAction(PostLevelCompleteAction):
    def __init__(self, game: LiftUpGame, level_num: int, persistence: GameHistoryPersistence, next_level_action: Optional[PostLevelCompleteAction], replay_action: PostLevelCompleteAction, level_select_action: PostLevelCompleteAction, game_history_show_action: PostLevelCompleteAction):
        self.game = game
        self.level_num = level_num
        self.persistence = persistence
        self.next_level_action = next_level_action
        self.replay_action = replay_action
        self.level_select_action = level_select_action
        self.game_history_show_action = game_history_show_action

    def execute(self, level: Level):
        screen = pg.display.get_surface()
        final_penalty = level.status_bar.total_penalty

        level_name = f"level_{self.level_num}"
        level_history = [entry for entry in self.persistence.read_all() if entry.level == level_name]
        level_history.sort(key=lambda x: x.timestamp_epoch_seconds, reverse=True)

        title_font, score_font, header_font, row_font, button_font = pg.font.Font(None, 74), pg.font.Font(None, 60), pg.font.Font(None, 50), pg.font.Font(None, 32), pg.font.Font(None, 32)
        WHITE, GREY, GREEN, BLUE, RED, PURPLE, GOLD, BACKGROUND = (255, 255, 255), (150, 150, 150), (100, 200, 100), (100, 100, 200), (200, 100, 100), (170, 100, 200), (255, 215, 0), (30, 30, 30)

        buttons, button_width, button_height = [], 180, 60
        if self.next_level_action:
            buttons.append(("Next Level", GREEN, self.next_level_action))
        else:
            buttons.append(("Level Select", PURPLE, self.level_select_action))
        buttons.append(("Replay", BLUE, self.replay_action))
        buttons.append(("Show History", GREY, self.game_history_show_action))
        buttons.append(("Exit", RED, None))

        total_width = len(buttons) * button_width + (len(buttons) - 1) * 20
        start_x = (screen.get_width() - total_width) / 2
        button_rects = [(pg.Rect(start_x + i * (button_width + 20), screen.get_height() - 100, button_width, button_height), text, color, action) for i, (text, color, action) in enumerate(buttons)]

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.current_level = None
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    for rect, _, _, action in button_rects:
                        if rect.collidepoint(event.pos):
                            if action:
                                action.execute(level)
                            else:
                                self.game.current_level = None
                            running = False
                            break
            
            screen.fill(BACKGROUND)
            title_surf = title_font.render(f"Level {self.level_num} Complete!", True, GOLD)
            screen.blit(title_surf, title_surf.get_rect(center=(screen.get_width() / 2, 80)))
            score_text_surf = row_font.render("Your Penalty:", True, WHITE)
            screen.blit(score_text_surf, score_text_surf.get_rect(center=(screen.get_width() / 2, 160)))
            score_val_surf = score_font.render(f"{final_penalty:.2f}", True, GOLD)
            screen.blit(score_val_surf, score_val_surf.get_rect(center=(screen.get_width() / 2, 210)))
            
            y_offset = 300
            history_header_surf = header_font.render("Level History", True, WHITE)
            screen.blit(history_header_surf, history_header_surf.get_rect(center=(screen.get_width() / 2, y_offset)))
            y_offset += 50
            pg.draw.line(screen, GOLD, (100, y_offset), (screen.get_width() - 100, y_offset), 1)
            y_offset += 30
            for entry in level_history[:5]:
                date_str, penalty_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(entry.timestamp_epoch_seconds)), f"{entry.penalty:.2f}"
                date_surf, penalty_surf = row_font.render(date_str, True, GREY), row_font.render(penalty_str, True, WHITE)
                screen.blit(date_surf, date_surf.get_rect(center=(screen.get_width() / 2 - 100, y_offset)))
                screen.blit(penalty_surf, penalty_surf.get_rect(center=(screen.get_width() / 2 + 150, y_offset)))
                y_offset += 40

            for rect, text, color, _ in button_rects:
                pg.draw.rect(screen, color, rect, border_radius=10)
                text_surf = button_font.render(text, True, BACKGROUND if color != GREY else WHITE)
                screen.blit(text_surf, text_surf.get_rect(center=rect.center))

            pg.display.flip()
