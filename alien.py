"""外星人：使用经典像素画图案绘制，共三种造型。"""
import pygame

# 每行 11 个字符，'X' 表示实心像素
PATTERNS = (
    (  # 水母（最上排，最值钱）
        "...XX.XX...",
        ".XXXXXXXXX.",
        "XXXXXXXXXXX",
        "XXX.XXX.XXX",
        "XXXXXXXXXXX",
        "...X...X...",
        "..X.....X..",
        ".X.......X.",
    ),
    (  # 螃蟹
        "....XXX....",
        "...XXXXX...",
        "..XXXXXXX..",
        ".XX.XXX.XX.",
        "XXXXXXXXXXX",
        "X.XXXXXXX.X",
        "X.X.....X.X",
        "...XX.XX...",
    ),
    (  # 章鱼
        "..XXXXXXX..",
        ".XXXXXXXXX.",
        "XXX.XXX.XXX",
        "XXXXXXXXXXX",
        "...XX.XX...",
        "..XX...XX..",
        ".XX.....XX.",
        "XX.......XX",
    ),
)

COLORS = (
    (255, 108, 108),  # 红
    (255, 196, 84),   # 橙
    (120, 208, 255),  # 蓝
)

_CACHE = {}


def render_pattern(type_index: int, pixel: int) -> pygame.Surface:
    """把像素画图案放大渲染成 Surface（带缓存）。"""
    key = (type_index, pixel)
    if key in _CACHE:
        return _CACHE[key]
    pattern = PATTERNS[type_index]
    color = COLORS[type_index]
    rows, cols = len(pattern), len(pattern[0])
    surf = pygame.Surface((cols * pixel, rows * pixel), pygame.SRCALPHA)
    for r, line in enumerate(pattern):
        for c, ch in enumerate(line):
            if ch == "X":
                pygame.draw.rect(surf, color, (c * pixel, r * pixel, pixel, pixel))
    _CACHE[key] = surf
    return surf


class Alien(pygame.sprite.Sprite):
    """单个外星人。"""

    def __init__(self, ai_game, type_index: int):
        super().__init__()
        self.screen = ai_game.screen
        self.type_index = type_index
        self.points = ai_game.settings.alien_points[type_index]
        self.image = render_pattern(type_index, ai_game.settings.alien_pixel)
        self.rect = self.image.get_rect()

    def update(self, dx: float):
        """按给定的水平位移移动。"""
        self.rect.x += dx

    def draw(self):
        self.screen.blit(self.image, self.rect)
