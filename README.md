# 外星人入侵（Alien Invasion）

一款用 **Python + pygame** 编写的经典街机射击游戏。玩家驾驶飞船保卫地球，消灭一波又一波的外星舰队。

## 玩法与规则

- 飞船出现在屏幕底部中央；
- **← → 方向键** 左右移动，**空格键** 射击（按住可连发，同屏最多 3 发子弹）；
- 外星舰队在天上排成一排并左右移动，触边后向下沉；舰队剩余越少移动越快；
- 消灭全部外星人后进入下一关——外星人移动更快、下落更快、分值更高；
- 外星人撞到飞船 **或** 有外星人到达屏幕底部 → 损失一艘飞船（共 3 艘，损失后短暂无敌重生）；
- 损失 3 艘飞船后游戏结束；最高分会保存在 `high_score.json`。

快捷键：`P` 暂停 / 继续，`Esc` 退出，`Enter` 或点击按钮开始 / 重新开始。

## 一、终端直接运行

```bash
# 1. 安装依赖（Python 3.14 用户请安装 pygame-ce，API 与 pygame 一致）
pip install pygame-ce        # 或 pip install -r requirements.txt

# 2. 生成音效资源（只需一次；若 assets/sounds 下已有 wav 可跳过）
python generate_assets.py

# 3. 运行游戏
python alien_invasion.py
```

## 二、直接打开运行的 exe（打包好的一键运行版）

无需安装 Python，双击即玩：

```
dist\外星人入侵.exe
```

- 单文件绿色程序（约 17 MB），音效等资源已内置；
- 双击启动；首次运行如提示安全软件拦截，请选择“允许”；
- 崩溃时会自动在 exe 旁边生成 `error.log` 便于排查。

## 三、自行打包 exe（可选）

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name "外星人入侵" --icon assets\icon.ico ^
    --add-data "assets;assets" alien_invasion.py
```

产物在 `dist\外星人入侵.exe`。

## 四、开发与自测

```bash
# 无头冒烟测试：跑 150 帧主循环，验证初始化/渲染/资源加载
python alien_invasion.py --smoke-test

# 逻辑自测：舰队生成、射击碰撞、过关提速、损失飞船、游戏结束、重开
python test_logic.py

# 重新生成音效（wave + math 标准库合成，无第三方依赖）
python generate_assets.py
```

## 项目结构

```
alien_game/
├── alien_invasion.py      # 主程序：主循环、事件、舰队与关卡逻辑
├── settings.py            # 全部可调参数（速度、子弹、编队、升级倍率…）
├── ship.py                # 飞船（移动、无敌闪烁、尾焰）
├── bullet.py              # 子弹
├── alien.py               # 外星人（三种经典像素画造型，按行排布）
├── game_stats.py          # 得分、生命、关卡、最高分持久化
├── scoreboard.py          # 计分板与生命图标
├── button.py              # 开始 / 重新开始按钮
├── utils.py               # 字体（中文）、音效、资源路径、崩溃日志
├── generate_assets.py    # 生成音效资源
├── test_logic.py          # 逻辑自测（8 项）
├── assets/
│   ├── icon.ico           # exe 图标
│   └── sounds/*.wav       # 射击 / 爆炸 / 受击 / 过关 / 行军音效
├── requirements.txt
└── dist/
    └── 外星人入侵.exe      # 双击即玩的单文件版本
```

## 实现说明

- 画面元素（飞船、外星人、星空、子弹）全部用 pygame 绘制/合成，无外部素材依赖；
- 外星人分三种像素画造型，分值与移动速度随关卡递增：`speedup_scale=1.16`、`score_scale=1.5`；
- 帧率锁定 60 FPS；无音频设备时游戏自动静音降级，不影响运行。
