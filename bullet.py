"""玩家子弹。"""
import pygame


class Bullet(pygame.sprite.Sprite):
    """从飞船顶部射出的子弹。"""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.rect = pygame.Rect(0, 0, self.settings.bullet_width, self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop
        self.y = float(self.rect.y)

    def update(self):
        """向上移动。"""
        self.y -= self.settings.bullet_speed
        self.rect.y = round(self.y)

    def draw(self):
        """绘制带亮芯的子弹。"""
        pygame.draw.rect(self.screen, self.settings.bullet_color, self.rect, border_radius=2)
        core = self.rect.inflate(-2, -8)
        pygame.draw.rect(self.screen, (235, 255, 242), core, border_radius=1)
