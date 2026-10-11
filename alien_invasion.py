"""外星人入侵 —— 一款使用 Pygame 编写的经典射击游戏。

玩法：
    * 左右方向键移动飞船，空格键射击（可按住连发）
    * 消灭屏幕中所有外星人后进入下一关，外星人移动更快
    * 外星人撞到飞船或到达屏幕底部，损失一艘飞船
    * 损失 3 艘飞船后游戏结束；P 键暂停，Esc 退出

运行：
    python alien_invasion.py
"""
import math
import os
import random
import sys

# 冒烟测试：无窗口跑若干帧，用于验证代码与打包产物可用
SMOKE_TEST = "--smoke-test" in sys.argv
if SMOKE_TEST:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from alien import Alien
from button import Button
from bullet import Bullet
from game_stats import GameStats
from scoreboard import Scoreboard
from settings import Settings
from ship import Ship
from utils import init_audio, install_excepthook, load_font, load_sound, play_sound, safe_print

SMOKE_FRAMES = 150


class AlienInvasion:
    """管理游戏资源与行为的主类。"""

    def __init__(self):
        pygame.init()
        self.settings = Settings()
        pygame.display.set_caption(self.settings.game_title)
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()

        self.stats = GameStats(self.settings)
        self.scoreboard = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self.start_button = Button(self, "开始游戏")
        self.restart_button = Button(self, "重新开始")

        self.game_state = "menu"  # menu / playing / gameover
        self.paused = False

        self._last_shot_ms = 0
        self._next_march_ms = 0
        self._march_toggle = False
        self._flash_until = 0
        self._stars = self._build_stars()
        self._title_font = load_font(72, bold=True)
        self._overlay_font = load_font(56, bold=True)
        self._hint_font = load_font(24)
        self._flash_surf = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)

        init_audio()
        self._create_fleet()

    # ---------------------------------------------------------- 主循环
    def run_game(self):
        frames = 0
        while True:
            self._handle_events()
            if self.game_state == "playing" and not self.paused:
                self._update_game()
            self._update_screen()
            self.clock.tick(self.settings.fps)

            frames += 1
            if SMOKE_TEST and frames >= SMOKE_FRAMES:
                self._finish_smoke_test()
                return

    def _finish_smoke_test(self):
        # 验证打包后的音效资源可用
        loaded = sum(1 for name in ("shoot", "explosion", "hit", "levelup", "march1", "march2")
                     if load_sound(name) is not None)
        try:
            with open("smoke_test_result.txt", "w", encoding="utf-8") as f:
                f.write(f"smoke test ok; sounds={loaded}/6")
        except OSError:
            pass
        safe_print("SMOKE TEST OK")
        pygame.quit()

    # ---------------------------------------------------------- 事件
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()
            elif event.type == pygame.KEYDOWN:
                self._on_key_down(event)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.ship.moving_left = False
                elif event.key == pygame.K_RIGHT:
                    self.ship.moving_right = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_click(event.pos)

        # 按住空格持续射击（带冷却）
        if self.game_state == "playing" and not self.paused:
            keys = pygame.key.get_pressed()
            now = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and now - self._last_shot_ms >= self.settings.bullet_cooldown_ms:
                self._fire_bullet()

    def _on_key_down(self, event):
        if event.key == pygame.K_ESCAPE:
            self._quit()
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_p and self.game_state == "playing":
            self.paused = not self.paused
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.game_state in ("menu", "gameover"):
                self._start_game()

    def _on_click(self, pos):
        if self.game_state == "menu" and self.start_button.rect.collidepoint(pos):
            self._start_game()
        elif self.game_state == "gameover" and self.restart_button.rect.collidepoint(pos):
            self._start_game()

    def _quit(self):
        self.stats.save_high_score()
        pygame.quit()
        sys.exit()

    # ---------------------------------------------------------- 游戏流程
    def _start_game(self):
        """从菜单/游戏结束进入新一局。"""
        if self.game_state == "gameover":
            self.stats.reset()
            self.settings.reset()
        self.game_state = "playing"
        self.paused = False
        self.bullets.empty()
        self.ship.reset_position()
        self.ship.moving_left = False
        self.ship.moving_right = False
        self._create_fleet()
        self.scoreboard.prep_images()

    def _game_over(self):
        self.game_state = "gameover"
        self.paused = False
        self.ship.moving_left = False
        self.ship.moving_right = False
        self.stats.save_high_score()

    def _update_game(self):
        now = pygame.time.get_ticks()
        self.ship.update()
        self._update_bullets()
        self._update_aliens(now)
        self._play_march(now)

    # ---------------------------------------------------------- 子弹
    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            self.bullets.add(Bullet(self))
            self._last_shot_ms = pygame.time.get_ticks()
            play_sound("shoot", 0.3)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.sprites():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            points = sum(alien.points
                         for group in collisions.values() for alien in group)
            self.stats.add_score(points)
            self.scoreboard.prep_images()
            play_sound("explosion", 0.4)

        if not self.aliens and self.game_state == "playing":
            self._next_level()

    def _next_level(self):
        """整批外星人被消灭：提速、加分、刷新编队。"""
        self.settings.increase_level()
        self.stats.level += 1
        self.bullets.empty()
        self._create_fleet()
        self.scoreboard.prep_images()
        play_sound("levelup", 0.5)

    # ---------------------------------------------------------- 外星人
    def _create_fleet(self):
        """创建一群外星人，横向居中、置于屏幕上方。"""
        self.aliens.empty()
        sample = Alien(self, 0)
        width, height = sample.rect.size
        gap_x, gap_y = self.settings.alien_gap_x, self.settings.alien_gap_y
        fleet_width = (self.settings.fleet_cols * width
                       + (self.settings.fleet_cols - 1) * gap_x)
        start_x = (self.settings.screen_width - fleet_width) // 2

        for row in range(self.settings.fleet_rows):
            type_index = 0 if row == 0 else (1 if row <= 2 else 2)
            for col in range(self.settings.fleet_cols):
                alien = Alien(self, type_index)
                alien.rect.x = start_x + col * (width + gap_x)
                alien.rect.y = self.settings.fleet_top_y + row * (height + gap_y)
                self.aliens.add(alien)

    def _update_aliens(self, now):
        if not self.aliens:
            return
        # 编队剩余越少，移动越快（营造紧张感）
        total = self.settings.fleet_rows * self.settings.fleet_cols
        boost = 1.0 + self.settings.kill_speedup * (total - len(self.aliens)) / total
        boost = min(boost, self.settings.max_alien_speed / self.settings.alien_speed)
        dx = self.settings.alien_speed * boost * self.settings.fleet_direction
        self.aliens.update(dx)
        self._check_fleet_edges()

        if not self.ship.invincible and pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        else:
            self._check_aliens_bottom()

    def _check_fleet_edges(self):
        margin = self.settings.fleet_edge_margin
        hit_edge = any(alien.rect.left <= margin
                       or alien.rect.right >= self.screen_rect.right - margin
                       for alien in self.aliens)
        if hit_edge:
            self.settings.fleet_direction *= -1
            for alien in self.aliens:
                alien.rect.y += self.settings.fleet_drop_speed

    def _check_aliens_bottom(self):
        for alien in self.aliens:
            if alien.rect.bottom >= self.screen_rect.bottom - 4:
                self._ship_hit()
                break

    def _ship_hit(self):
        """外星人撞到飞船或到达底部：损失一艘飞船。"""
        self.stats.ships_left -= 1
        self.scoreboard.prep_images()
        self._flash_until = pygame.time.get_ticks() + 300
        play_sound("hit", 0.5)

        if self.stats.ships_left <= 0:
            self._game_over()
            return

        self.ship.reset_position()
        self.ship.hit()  # 短暂无敌
        self.bullets.empty()
        self._create_fleet()

    def _play_march(self, now):
        """外星人行军音效：随关卡变快，双音交替。"""
        if not self.aliens or self.game_state != "playing":
            return
        if now < self._next_march_ms:
            return
        interval = max(220, 560 - (self.stats.level - 1) * 35)
        self._next_march_ms = now + interval
        play_sound("march2" if self._march_toggle else "march1", 0.16)
        self._march_toggle = not self._march_toggle

    # ---------------------------------------------------------- 画面
    def _build_stars(self):
        stars = []
        for _ in range(90):
            x = random.randrange(0, self.settings.screen_width)
            y = random.randrange(0, self.settings.screen_height)
            radius = random.choice((1, 1, 1, 2))
            brightness = random.randrange(90, 210)
            stars.append((x, y, radius, brightness))
        return stars

    def _draw_background(self):
        self.screen.fill(self.settings.bg_color)
        now = pygame.time.get_ticks() / 1000.0
        for i, (x, y, radius, brightness) in enumerate(self._stars):
            twinkle = int(brightness + 40 * ((i % 5) / 5.0 - 0.5)
                          * math.sin(now * 2 + i))
            twinkle = max(40, min(255, twinkle))
            pygame.draw.circle(self.screen, (twinkle, twinkle, twinkle + 20),
                               (x, y), radius)

    def _draw_center_text(self, text, font, color, y_offset=0):
        image = font.render(text, True, color)
        rect = image.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery + y_offset))
        self.screen.blit(image, rect)

    def _update_screen(self):
        self._draw_background()

        if self.game_state == "menu":
            self._draw_menu()
        elif self.game_state == "gameover":
            self._draw_game()
            self._draw_game_over()
        else:
            self._draw_game()
            if self.paused:
                self._draw_pause()

        pygame.display.flip()

    def _draw_game(self):
        for bullet in self.bullets.sprites():
            bullet.draw()
        for alien in self.aliens.sprites():
            alien.draw()
        self.ship.draw()
        self.scoreboard.show_score()
        # 受击红闪
        remaining = self._flash_until - pygame.time.get_ticks()
        if remaining > 0:
            alpha = max(0, min(140, int(remaining * 0.9)))
            self._flash_surf.fill((210, 40, 40, alpha))
            self.screen.blit(self._flash_surf, (0, 0))

    def _draw_menu(self):
        title = self._title_font.render(self.settings.game_title, True, (140, 255, 190))
        title_rect = title.get_rect(
            center=(self.screen_rect.centerx, self.screen_rect.centery - 130))
        # 标题发光
        glow = pygame.Surface(title.get_rect().size, pygame.SRCALPHA)
        glow.blit(title, (0, 0))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            self.screen.blit(glow, title_rect.move(dx, dy))
        self.screen.blit(title, title_rect)

        self._draw_center_text("保卫地球，击退外星入侵者！",
                               self._hint_font, (200, 210, 225), -62)
        self.start_button.draw()
        self._draw_center_text(
            "← → 移动    空格键射击    P 暂停    Esc 退出",
            self._hint_font, (170, 180, 200), 130)

    def _draw_game_over(self):
        overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        self._draw_center_text("游戏结束", self._overlay_font, (255, 96, 96), -110)
        self._draw_center_text(
            f"本局得分 {self.stats.score:,}    最高分 {self.stats.high_score:,}",
            self._hint_font, (235, 240, 250), -46)
        self.restart_button.draw()
        self._draw_center_text("点击按钮或按 Enter 重新开始",
                               self._hint_font, (170, 180, 200), 110)

    def _draw_pause(self):
        overlay = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        self._draw_center_text("已暂停", self._overlay_font, (255, 214, 96), -30)
        self._draw_center_text("按 P 继续", self._hint_font, (220, 226, 240), 34)


def main():
    install_excepthook()
    game = AlienInvasion()
    game.run_game()


if __name__ == "__main__":
    main()
