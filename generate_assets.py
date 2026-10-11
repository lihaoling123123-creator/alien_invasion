"""生成游戏音效资源（assets/sounds/*.wav），只用标准库，不依赖第三方库。

用法：
    python generate_assets.py
"""
import math
import os
import random
import struct
import wave

RATE = 44100
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")


def write_wav(name: str, samples):
    """把 [-1, 1] 的浮点采样写成 16bit 单声道 WAV。"""
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name + ".wav")
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples)
        f.writeframes(frames)
    return path


def _envelope(i: int, n: int, attack: float = 0.01):
    """线性起音 + 幂次衰减的包络。"""
    t = i / n
    a = min(1.0, (i + 1) / max(attack * n, 1))
    return a * (1.0 - t) ** 1.6


def make_shoot():
    """射击：高频向低频滑落的方波。"""
    n = int(RATE * 0.14)
    out, phase = [], 0.0
    for i in range(n):
        t = i / n
        freq = 950 - 700 * t
        phase += 2 * math.pi * freq / RATE
        wave_val = 1.0 if math.sin(phase) >= 0 else -1.0
        out.append(wave_val * 0.32 * _envelope(i, n))
    return out


def make_explosion():
    """爆炸：噪声 + 下滑正弦。"""
    n = int(RATE * 0.3)
    out, prev, phase = [], 0.0, 0.0
    for i in range(n):
        t = i / n
        noise = random.uniform(-1.0, 1.0)
        prev = 0.55 * prev + 0.45 * noise          # 一阶低通，闷一点
        freq = 220 - 150 * t
        phase += 2 * math.pi * freq / RATE
        out.append((prev * 0.55 + 0.35 * math.sin(phase)) * (1 - t) ** 1.8 * 0.7)
    return out


def make_hit():
    """飞船被撞：长声下滑锯齿波。"""
    n = int(RATE * 0.45)
    out, phase = [], 0.0
    for i in range(n):
        t = i / n
        freq = 420 - 340 * t
        phase += freq / RATE
        saw = (phase % 1.0) * 2.0 - 1.0
        out.append(saw * 0.4 * _envelope(i, n, attack=0.002))
    return out


def make_levelup():
    """过关：上行三连音。"""
    out = []
    for freq in (523.0, 659.0, 784.0, 1046.0):
        n = int(RATE * 0.11)
        phase = 0.0
        for i in range(n):
            phase += 2 * math.pi * freq / RATE
            out.append(math.sin(phase) * 0.32 * _envelope(i, n, attack=0.02))
    return out


def make_march(base_freq: float):
    """外星人行军的短促低音。"""
    n = int(RATE * 0.075)
    out, phase = [], 0.0
    for i in range(n):
        phase += 2 * math.pi * base_freq / RATE
        wave_val = 1.0 if math.sin(phase) >= 0 else -1.0
        out.append(wave_val * 0.22 * _envelope(i, n, attack=0.004))
    return out


def main():
    files = [
        write_wav("shoot", make_shoot()),
        write_wav("explosion", make_explosion()),
        write_wav("hit", make_hit()),
        write_wav("levelup", make_levelup()),
        write_wav("march1", make_march(110.0)),
        write_wav("march2", make_march(98.0)),
    ]
    for path in files:
        print("generated:", path)


if __name__ == "__main__":
    main()
