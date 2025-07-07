import sys
import pygame
from pygame import Surface, KEYDOWN, K_ESCAPE
from pygame.font import Font

from code.Const import C_YELLOW, SCORE_POS, MENU_OPTION, C_WHITE
from code.DBProxy import DBProxy


class GameOver:
    def __init__(self, window: Surface):
        self.window = window
        self.surf = pygame.image.load('./asset/GameOverBg.png').convert_alpha()
        self.rect = self.surf.get_rect(left=0, top=0)

    def show(self, player_score: list, game_mode: str):
        pygame.mixer_music.load('./asset/GameOver.wav')
        pygame.mixer_music.play(1)

        # Safe conversion function for scores
        def safe_int(value, default=0):
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Convert scores safely
        player1_score = safe_int(player_score[0])
        player2_score = safe_int(player_score[1])

        # Vertical offset to move everything up by 30 pixels
        offset_y = -30

        while True:
            self.window.blit(source=self.surf, dest=self.rect)

            # Display player scores with offset
            if game_mode == MENU_OPTION[0]:  # 1P Mode
                self.game_over_text(20, f'Your Score: {player1_score:05d}', C_WHITE,
                                    (SCORE_POS[0][0], SCORE_POS[0][1]))

            elif game_mode == MENU_OPTION[1]:  # Cooperative
                team_score = (player1_score + player2_score) // 2
                self.game_over_text(20, f'Team Score: {team_score:05d}', C_WHITE,
                                    (SCORE_POS[0][0], SCORE_POS[0][1] + offset_y))
                self.game_over_text(20, f'Player 1: {player1_score:05d}', C_WHITE,
                                    (SCORE_POS[1][0], SCORE_POS[1][1] + offset_y))
                self.game_over_text(20, f'Player 2: {player2_score:05d}', C_WHITE,
                                    (SCORE_POS[2][0], SCORE_POS[2][1] + offset_y))

            elif game_mode == MENU_OPTION[2]:  # Competitive
                winner_score = max(player1_score, player2_score)
                self.game_over_text(20, f'Winner Score: {winner_score:05d}', C_WHITE,
                                    (SCORE_POS[0][0], SCORE_POS[0][1] + offset_y))
                self.game_over_text(20, f'Player 1: {player1_score:05d}', C_WHITE,
                                    (SCORE_POS[1][0], SCORE_POS[1][1] + offset_y))
                self.game_over_text(20, f'Player 2: {player2_score:05d}', C_WHITE,
                                    (SCORE_POS[2][0], SCORE_POS[2][1] + offset_y))

            # Display top scores
            self.game_over_text(20, 'TOP 10 SCORES:', C_YELLOW,
                                (SCORE_POS['Label'][0], SCORE_POS[3][1] + offset_y))

            db_proxy = DBProxy('DBScore')
            try:
                list_score = db_proxy.retrieve_top10()
                for i, score_entry in enumerate(list_score[:6]):  # Show first 6 to fit
                    id_, name, score, date = score_entry
                    self.game_over_text(20, f'{name} {safe_int(score):05d}', C_YELLOW,
                                        (SCORE_POS['Label'][0], SCORE_POS[i + 4][1] + offset_y))
                    self.game_over_text(20, 'Press ESC to return to menu', C_WHITE,
                                        (SCORE_POS['Label'][0], SCORE_POS[9][1] + offset_y + 30))
            finally:
                db_proxy.close()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    return

            pygame.display.flip()

    def game_over_text(self, text_size: int, text: str, text_color: tuple, text_pos: tuple):
        text_font: Font = pygame.font.SysFont(name="Lucida Sans Typewriter", size=text_size)
        text_surf = text_font.render(text, True, text_color).convert_alpha()
        text_rect = text_surf.get_rect(center=text_pos)
        self.window.blit(source=text_surf, dest=text_rect)