"""外星人入侵：全局设置（固定配置 + 随关卡变化的运行时配置）。"""


class Settings:
    """管理游戏的所有设置，运行时数值随关卡提升而变化。"""

    # ---------- 屏幕 ----------
    screen_width = 1000
    screen_height = 700
    fps = 60
    bg_color = (12, 12, 30)
    game_title = "外星人入侵"

    # ---------- 飞船 ----------
    ship_speed = 6.5
    ship_limit = 3                 # 玩家一共拥有的飞船数量
    ship_invincible_seconds = 2.0  # 损失飞船后的短暂无敌时间

    # ---------- 子弹 ----------
    bullet_speed = 11.0
    bullet_width = 5
    bullet_height = 18
    bullet_color = (120, 255, 160)
    bullets_allowed = 3            # 屏幕上同时最多存在的子弹数
    bullet_cooldown_ms = 260       # 连续射击的最小间隔

    # ---------- 外星人编队 ----------
    fleet_rows = 5
    fleet_cols = 9
    alien_pixel = 4                # 像素画放大倍数
    alien_gap_x = 52
    alien_gap_y = 34
    fleet_top_y = 92
    fleet_edge_margin = 8          # 距屏幕左右边缘多少像素算“碰壁”

    # ---------- 关卡升级 ----------
    speedup_scale = 1.16           # 每过一关，外星人水平移动速度倍率
    drop_scale = 1.08              # 每过一关，外星人下落速度倍率
    score_scale = 1.5              # 每过一关，外星人分值倍率
    max_alien_speed = 7.5
    max_drop_speed = 90
    base_alien_points = (30, 20, 10)  # 三类外星人的基础分值（越靠上越值钱）
    kill_speedup = 0.8             # 编队剩余越少，剩余外星人越快（最多加速的比例）

    def __init__(self):
        self.reset()

    def reset(self):
        """新开一局时恢复初始运行时数值。"""
        self.alien_speed = 1.15
        self.fleet_drop_speed = 30
        self.fleet_direction = 1  # 1 向右，-1 向左
        self.alien_points = list(self.base_alien_points)

    def increase_level(self):
        """消灭整批外星人后提速并提高分值。"""
        self.alien_speed = min(self.alien_speed * self.speedup_scale, self.max_alien_speed)
        self.fleet_drop_speed = min(self.fleet_drop_speed * self.drop_scale, self.max_drop_speed)
        self.alien_points = [int(round(p * self.score_scale)) for p in self.alien_points]
        self.fleet_direction = 1
