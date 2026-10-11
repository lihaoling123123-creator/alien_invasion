"""游戏状态统计：生命、分数、关卡，以及最高分的本地持久化。"""
import json
import os
import sys


class GameStats:
    """跟踪游戏的统计信息（得分、剩余飞船、关卡、最高分）。"""

    def __init__(self, settings):
        self.settings = settings
        self.high_score_path = self._high_score_path()
        self.high_score = self._load_high_score()
        self.reset()

    # ---------- 最高分持久化 ----------
    def _high_score_path(self):
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "high_score.json")

    def _load_high_score(self):
        try:
            with open(self.high_score_path, encoding="utf-8") as f:
                return int(json.load(f).get("high_score", 0))
        except (OSError, ValueError):
            return 0

    def save_high_score(self):
        try:
            with open(self.high_score_path, "w", encoding="utf-8") as f:
                json.dump({"high_score": self.high_score}, f)
        except OSError:
            pass

    # ---------- 局内状态 ----------
    def reset(self):
        """重置一局游戏的统计信息。"""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def add_score(self, points):
        """累加分数；若刷新最高分则立即写入文件。"""
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
