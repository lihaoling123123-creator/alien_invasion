"""计分板：分数、最高分、关卡与剩余飞船。"""
import pygame

from ship import build_ship_surface
from utils import load_font


class Scoreboard:
    """在屏幕上显示得分、最高分、关卡和剩余飞船数量。"""

    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen_rect
        self.settings = ai_game.settings
        self.stats = ai_game.stats
        self.text_color = (228, 236, 246)
        self.accent_color = (255, 214, 96)
        self.font = load_font(26)
        self.big_font = load_font(34, bold=True)
        self.lives_image = build_ship_surface(0.5)
        self.prep_images()

    def prep_images(self):
        """根据当前统计信息重新渲染各元素。"""
        self.score_image = self.big_font.render(
            f"分数 {self.stats.score:,}", True, self.text_color)
        self.score_rect = self.score_image.get_rect()
        self.score_rect.midtop = (self.screen_rect.centerx, 12)

        self.high_image = self.font.render(
            f"最高分 {self.stats.high_score:,}", True, self.accent_color)
        self.high_rect = self.high_image.get_rect()
        self.high_rect.midtop = (self.screen_rect.centerx, self.score_rect.bottom + 4)

        self.level_image = self.font.render(
            f"第 {self.stats.level} 关", True, self.text_color)
        self.level_rect = self.level_image.get_rect()
        self.level_rect.bottomright = (self.screen_rect.right - 18,
                                       self.screen_rect.bottom - 14)

        self.lives_rect = self.lives_image.get_rect()
        self.lives_rect.bottomleft = (18, self.screen_rect.bottom - 10)

    def show_score(self):
        """把分数、最高分、关卡和生命图标绘制到屏幕上。"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_image, self.high_rect)
        self.screen.blit(self.level_image, self.level_rect)
        x = self.lives_rect.left
        for _ in range(self.stats.ships_left):
            self.screen.blit(self.lives_image, (x, self.lives_rect.y))
            x += self.lives_rect.width + 8
