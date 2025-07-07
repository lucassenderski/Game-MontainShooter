import sys
from datetime import datetime

import pygame
from pygame import Surface, Rect, KEYDOWN, K_RETURN, K_BACKSPACE, K_ESCAPE
from pygame.font import Font

from code.Const import C_YELLOW, SCORE_POS, MENU_OPTION, C_WHITE
from code.DBProxy import DBProxy


class Score:
    def __init__(self, window: Surface):
        self.window = window
        self.surf = pygame.image.load('./asset/ScoreBg.png').convert_alpha()
        self.rect = self.surf.get_rect(left=0, top=0)

    def save(self, game_mode: str, player_score: list):
        pygame.mixer_music.load('./asset/Score.mp3')
        pygame.mixer_music.play(-1)
        db_proxy = DBProxy('DBScore')
        name = ''
        max_length = 5  # Definindo o tamanho máximo do nome

        # Garante que os scores são inteiros
        try:
            player_score[0] = int(player_score[0])
            player_score[1] = int(player_score[1])
        except (ValueError, TypeError):
            player_score = [0, 0]

        while True:
            self.window.blit(source=self.surf, dest=self.rect)
            self.score_text(48, 'YOU WIN!!', C_YELLOW, SCORE_POS['Title'])

            # Calcula o score e texto de instrução
            if game_mode == MENU_OPTION[0]:  # 1P
                score = player_score[0]
                text = 'Enter Player 1 name (5 characters max):'
            elif game_mode == MENU_OPTION[1]:  # 2P Cooperativo
                score = (player_score[0] + player_score[1]) // 2
                text = 'Enter Team name (5 characters max):'
            elif game_mode == MENU_OPTION[2]:  # 2P Competitivo
                score = max(player_score[0], player_score[1])
                text = 'Enter Winner name (5 characters max):'
                if player_score[1] > player_score[0]:
                    text = 'Enter Player 2 name (5 characters max):'

            self.score_text(20, text, C_WHITE, SCORE_POS['EnterName'])
            self.score_text(20, name, C_WHITE, SCORE_POS['Name'])

            # Adiciona mensagem de instrução
            self.score_text(16, 'Press ENTER to confirm or ESC to cancel', C_WHITE,
                            (SCORE_POS['Label'][0], SCORE_POS[9][1] + 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_RETURN and len(name) > 0:  # Alterado para aceitar de 1 a 5 caracteres
                        db_proxy.save({
                            'name': name[:max_length],  # Garante o tamanho máximo
                            'score': int(score),
                            'date': get_formatted_date()
                        })
                        self.show()
                        return
                    elif event.key == K_ESCAPE:  # Permite sair sem salvar
                        return
                    elif event.key == K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < max_length and event.unicode.isalnum():  # Aceita apenas caracteres alfanuméricos
                        name += event.unicode

            pygame.display.flip()

    def show(self):
        pygame.mixer_music.load('./asset/Score.mp3')
        pygame.mixer_music.play(-1)
        self.window.blit(source=self.surf, dest=self.rect)
        self.score_text(48, 'TOP 10 SCORE', C_YELLOW, SCORE_POS['Title'])
        self.score_text(20, 'NAME     SCORE           DATE      ', C_YELLOW, SCORE_POS['Label'])

        db_proxy = DBProxy('DBScore')
        try:
            list_score = db_proxy.retrieve_top10()
            for i, player_score in enumerate(list_score):
                id_, name, score, date = player_score
                # Formata o score com 5 dígitos, preenchendo com zeros à esquerda
                self.score_text(20, f'{name}     {int(score):05d}     {date}',
                                C_YELLOW, SCORE_POS[i])
                self.score_text(20, 'Press ESC to return to menu', C_WHITE,(SCORE_POS['Label'][0], SCORE_POS[9][1] +20))
        finally:
            db_proxy.close()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
            pygame.display.flip()


    def score_text(self, text_size: int, text: str, text_color: tuple, text_center_pos: object = tuple):
        text_font: Font = pygame.font.SysFont(name="Lucida Sans Typewriter", size=text_size)
        text_surf: Surface = text_font.render(text, True, text_color).convert_alpha()
        text_rect: Rect = text_surf.get_rect(center=text_center_pos)
        self.window.blit(source=text_surf, dest=text_rect)


def get_formatted_date():
    current_datetime = datetime.now()
    return current_datetime.strftime("%H:%M - %d/%m/%y")