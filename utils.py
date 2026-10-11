"""通用工具：资源路径、中文字体、音效加载与播放、崩溃日志。"""
import os
import sys

import pygame


def resource_path(relative_path: str) -> str:
    """兼容 PyInstaller 打包后的资源路径。"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


_FONT_CANDIDATES = (
    "microsoftyahei", "msyh", "msyhbd", "simhei", "simsun",
    "pingfangsc", "pingfang", "notosanscjksc", "notosanscjk",
    "wenquanyimicrohei", "droidsansfallback", "arialunicodems",
)


def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """加载支持中文的字体，找不到时回退到系统默认字体。"""
    for name in _FONT_CANDIDATES:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.SysFont(None, size)


_SOUND_CACHE = {}
_AUDIO_OK = False


def init_audio() -> bool:
    """初始化混音器；没有音频设备时静默降级，保证游戏仍可运行。"""
    global _AUDIO_OK
    if _AUDIO_OK:
        return True
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(16)
        _AUDIO_OK = True
    except pygame.error:
        _AUDIO_OK = False
    return _AUDIO_OK


def load_sound(name: str):
    """加载 assets/sounds/<name>.wav；失败时返回 None。"""
    if not _AUDIO_OK:
        return None
    if name in _SOUND_CACHE:
        return _SOUND_CACHE[name]
    sound = None
    path = resource_path(os.path.join("assets", "sounds", name + ".wav"))
    if os.path.exists(path):
        try:
            sound = pygame.mixer.Sound(path)
        except pygame.error:
            sound = None
    _SOUND_CACHE[name] = sound
    return sound


def play_sound(name: str, volume: float = 0.5) -> None:
    """播放一次音效（音量 0~1）。"""
    sound = load_sound(name)
    if sound is not None:
        sound.set_volume(volume)
        sound.play()


def safe_print(*args, **kwargs) -> None:
    """无控制台环境下（打包成窗口程序时）安全打印。"""
    if sys.stdout is None:
        return
    try:
        print(*args, **kwargs)
    except OSError:
        pass


def install_excepthook(log_name: str = "error.log") -> None:
    """窗口程序没有控制台，把崩溃信息写入日志文件便于排查。"""

    def _hook(exc_type, exc_value, exc_tb):
        try:
            import traceback
            if getattr(sys, "frozen", False):
                base = os.path.dirname(sys.executable)
            else:
                base = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(base, log_name), "a", encoding="utf-8") as f:
                f.write("".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
        except Exception:
            pass
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook
