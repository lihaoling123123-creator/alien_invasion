"""开发用逻辑自测：验证射击、碰撞、过关、生命与游戏结束流程。"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from alien_invasion import AlienInvasion


def new_game():
    g = AlienInvasion()
    g._start_game()
    return g


def main():
    # 1. 编队数量正确
    g = new_game()
    expected = g.settings.fleet_rows * g.settings.fleet_cols
    assert len(g.aliens) == expected, f"fleet size {len(g.aliens)} != {expected}"
    print(f"[1] fleet created: {len(g.aliens)} aliens OK")

    # 2. 子弹上限与射击
    g._fire_bullet()
    g._last_shot_ms = 0  # 绕过冷却
    g._fire_bullet()
    g._last_shot_ms = 0
    g._fire_bullet()
    g._last_shot_ms = 0
    g._fire_bullet()  # 第四发应被上限拦截
    assert len(g.bullets) == g.settings.bullets_allowed, "bullet cap failed"
    print(f"[2] bullet cap = {len(g.bullets)} OK")

    # 3. 子弹击中外星人：数量 -1、得分增加
    g.bullets.empty()
    bullet_hits(g)
    print(f"[3] collision: aliens={len(g.aliens)}, score={g.stats.score} OK")

    # 4. 清空全部外星人应升关、提速、分值提高
    g.bullets.empty()
    speed_before = g.settings.alien_speed
    points_before = g.settings.alien_points[0]
    for alien in list(g.aliens):
        g.bullets.add(_fake_bullet_on(g, alien))
    g._update_bullets()
    assert len(g.aliens) == expected, "fleet should respawn after clear"
    assert g.stats.level == 2, f"level {g.stats.level} != 2"
    assert g.settings.alien_speed > speed_before, "speed should increase"
    assert g.settings.alien_points[0] > points_before, "points should increase"
    print(f"[4] level up: lv={g.stats.level}, speed={g.settings.alien_speed:.2f}, "
          f"points={g.settings.alien_points} OK")

    # 5. 外星人到达屏幕底部 -> 损失一艘飞船并重置编队
    g.settings.ship_invincible_seconds = 0  # 测试时不无敌，便于连续验证
    lives_before = g.stats.ships_left
    lowest = max(a.rect.bottom for a in g.aliens)
    drop = g.screen_rect.bottom - lowest + 10
    for alien in g.aliens:
        alien.rect.y += drop
    g._check_aliens_bottom()
    assert g.stats.ships_left == lives_before - 1, "life not consumed"
    assert g.game_state == "playing"
    assert min(a.rect.top for a in g.aliens) >= 0, "fleet should reset to top"
    print(f"[5] aliens bottom: lives={g.stats.ships_left} OK")

    # 6. 飞船被撞 -> 损失飞船
    lives_before = g.stats.ships_left
    target = g.aliens.sprites()[0]
    target.rect.center = g.ship.rect.center
    g._update_aliens(pygame.time.get_ticks())
    assert g.stats.ships_left == lives_before - 1, "ship collision not detected"
    print(f"[6] ship collision: lives={g.stats.ships_left} OK")

    # 7. 连续损失飞船直到游戏结束
    while g.stats.ships_left > 0:
        g.settings.ship_invincible_seconds = 0
        g._ship_hit()
    assert g.game_state == "gameover", "should be game over"
    print(f"[7] game over reached, state={g.game_state} OK")

    # 8. 重新开始
    g._start_game()
    assert g.game_state == "playing" and g.stats.ships_left == g.settings.ship_limit
    assert g.stats.level == 1 and g.stats.score == 0
    assert len(g.aliens) == expected
    print(f"[8] restart OK: lives={g.stats.ships_left}, lv={g.stats.level}")

    pygame.quit()
    print("ALL LOGIC TESTS PASSED")


def _fake_bullet_on(g, alien):
    from bullet import Bullet
    b = Bullet(g)
    b.rect.center = alien.rect.center
    b.y = float(b.rect.y)
    return b


def bullet_hits(g):
    from bullet import Bullet
    target = g.aliens.sprites()[0]
    b = Bullet(g)
    b.rect.center = target.rect.center
    b.y = float(b.rect.y)
    g.bullets.add(b)
    g._update_bullets()
    assert len(g.aliens) == g.settings.fleet_rows * g.settings.fleet_cols - 1
    assert g.stats.score > 0


if __name__ == "__main__":
    sys.exit(main())
