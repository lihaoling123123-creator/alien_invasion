"""玩家飞船。"""
import pygame


def build_ship_surface(scale: float = 1.0) -> pygame.Surface:
    """绘制一艘小飞船（也用于计分板上的生命图标）。"""
    w, h = 84, 52
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body = (84, 224, 172)    # 机身主色
    edge = (28, 120, 96)     # 描边/机翼
    glow = (216, 255, 244)   # 座舱高光
    glass = (70, 170, 232)   # 座舱玻璃
    cx = w // 2
    hull = [
        (cx, 2), (cx + 12, 16), (cx + 20, 30),
        (w - 4, 38), (w - 4, 48), (4, 48), (4, 38),
        (cx - 20, 30), (cx - 12, 16),
    ]
    pygame.draw.polygon(surf, body, hull)
    pygame.draw.polygon(surf, edge, hull, 2)
    # 两侧机翼
    pygame.draw.rect(surf, edge, (2, 38, 20, 10), border_radius=3)
    pygame.draw.rect(surf, edge, (w - 22, 38, 20, 10), border_radius=3)
    pygame.draw.rect(surf, body, (4, 40, 16, 6), border_radius=2)
    pygame.draw.rect(surf, body, (w - 20, 40, 16, 6), border_radius=2)
    # 座舱
    pygame.draw.ellipse(surf, glow, (cx - 9, 12, 18, 20))
    pygame.draw.ellipse(surf, glass, (cx - 6, 15, 12, 14))
    if scale != 1.0:
        size = (max(1, int(w * scale)), max(1, int(h * scale)))
        surf = pygame.transform.smoothscale(surf, size)
    return surf


class Ship(pygame.sprite.Sprite):
    """受玩家控制的飞船。"""

    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen_rect
        self.settings = ai_game.settings
        self.image = build_ship_surface()
        self.rect = self.image.get_rect()
        self.moving_left = False
        self.moving_right = False
        self._invincible_until = 0
        self.reset_position()

    def reset_position(self):
        """回到屏幕底部中央。"""
        self.rect.midbottom = (self.screen_rect.centerx, self.screen_rect.bottom - 10)
        self.x = float(self.rect.x)

    def hit(self):
        """被外星人撞击后进入短暂无敌状态。"""
        self._invincible_until = pygame.time.get_ticks() + int(self.settings.ship_invincible_seconds * 1000)

    @property
    def invincible(self):
        return pygame.time.get_ticks() < self._invincible_until

    def update(self):
        """根据按键状态左右移动，不允许移出屏幕。"""
        if self.moving_left:
            self.x -= self.settings.ship_speed
        if self.moving_right:
            self.x += self.settings.ship_speed
        self.x = max(0.0, min(self.x, self.screen_rect.width - self.rect.width))
        self.rect.x = round(self.x)

    def draw(self):
        """绘制飞船；无敌期间闪烁。"""
        if self.invincible and (pygame.time.get_ticks() // 120) % 2 == 0:
            return
        self.screen.blit(self.image, self.rect)
        self._draw_flame()

    def _draw_flame(self):
        """尾焰（轻微闪动）。"""
        length = 7 + (pygame.time.get_ticks() // 70) % 3 * 4
        x, y = self.rect.centerx, self.rect.bottom - 2
        pygame.draw.polygon(
            self.screen, (255, 168, 60),
            [(x - 7, y), (x + 7, y), (x, y + length)])
        pygame.draw.polygon(
            self.screen, (255, 244, 140),
            [(x - 3, y), (x + 3, y), (x, y + length - 4)])
