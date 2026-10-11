"""开始/重新开始按钮。"""
import pygame

from utils import load_font


class Button:
    """屏幕中央的圆角矩形按钮（支持鼠标悬停高亮）。"""

    def __init__(self, ai_game, msg: str):
        self.screen = ai_game.screen
        self.rect = pygame.Rect(0, 0, 240, 64)
        self.rect.center = ai_game.screen_rect.center
        self.text_color = (14, 26, 20)
        self.bg_color = (120, 255, 160)
        self.hover_color = (170, 255, 195)
        self.border_color = (30, 70, 50)
        self.font = load_font(30, bold=True)
        self._prep_msg(msg)

    def _prep_msg(self, msg: str):
        self.msg_image = self.font.render(msg, True, self.text_color)
        self.msg_image_rect = self.msg_image.get_rect(center=self.rect.center)

    def draw(self):
        color = self.bg_color
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            color = self.hover_color
        pygame.draw.rect(self.screen, color, self.rect, border_radius=14)
        pygame.draw.rect(self.screen, self.border_color, self.rect, 3, border_radius=14)
        self.screen.blit(self.msg_image, self.msg_image_rect)
