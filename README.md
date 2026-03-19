# 天机 (tianji)

[![PyPI version](https://img.shields.io/pypi/v/tianji.svg)](https://pypi.org/project/tianji/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Zijian-Ni/tianji/actions/workflows/ci.yml/badge.svg)](https://github.com/Zijian-Ni/tianji/actions)

**天机** 是一个纯 Python 实现的中国玄学算法库，支持八字排盘、六爻起卦、紫微斗数等功能，并提供可选的大语言模型解读层。

> "天机不可泄露" — 但代码可以开源。

---

## 功能特性

- 🔢 **八字 (BaZi)** — 四柱排盘（年月日时），十神，五行分析，大运，刑冲合害
- 🎴 **六爻 (Liu Yao)** — 64卦起卦，装卦（世应、六亲、六神、动爻）
- ⭐ **紫微斗数 (Zi Wei Dou Shu)** — 十二宫，主星安星
- 🤖 **LLM 解读** — 可选接入 OpenAI，自动生成命盘解读
- 🌐 **REST API** — FastAPI 服务，便于集成
- 💻 **命令行工具** — `tianji bazi`, `tianji liuyao`

---

## 安装

```bash
pip install tianji
```

带 LLM 支持：

```bash
pip install "tianji[llm]"
```

---

## 快速开始

### 八字排盘

```python
from datetime import datetime
from tianji.bazi import BaZiChart

# 排四柱
chart = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30), gender="male")
chart.display()
```

输出示例：
```
╔══════════════════════════════════════╗
║         八字命盘 (BaZi Chart)         ║
╠═══════╦═══════╦═══════╦═══════╣
║  年柱  ║  月柱  ║  日柱  ║  时柱  ║
║  庚午  ║  辛巳  ║  丙申  ║  甲未  ║
╠═══════╬═══════╬═══════╬═══════╣
║ 日主: 丙火                           ║
║ 五行: 木1 火3 土1 金3 水0            ║
╚══════════════════════════════════════╝
```

### 六爻起卦

```python
from tianji.liuyao import cast_hexagram, LiuYaoAnalysis

# 时间起卦
result = cast_hexagram(method="time")
analysis = LiuYaoAnalysis(result)
analysis.display()
```

### 命令行

```bash
# 八字
tianji bazi --date 1990-05-15 --time 14:30 --gender male

# 六爻（时间起卦）
tianji liuyao --method time

# 启动 API 服务
tianji serve --port 8000
```

### REST API

```bash
uvicorn tianji.api.app:app --reload
```

```bash
# 八字排盘
curl -X POST http://localhost:8000/bazi/chart \
  -H "Content-Type: application/json" \
  -d '{"birth_datetime": "1990-05-15T14:30:00", "gender": "male"}'

# 六爻起卦
curl -X POST http://localhost:8000/liuyao/cast \
  -d '{"method": "time"}'
```

---

## 算法说明

### 八字

- **年柱**: 以 **立春** 为年界（非元旦/春节）
- **月柱**: 以节气为月界，五虎遁月法推算月干
- **日柱**: 以 1900-01-01 甲子日为参考，计算天数差模60
- **时柱**: 五鼠遁时法推算时干

### 六爻

- **六十四卦**: 8 × 8 卦，Unicode 符号 ☰☱☲☳☴☵☶☷
- 支持时间起卦、数字起卦、铜钱模拟

### 紫微斗数

- 十二宫（命宫、财帛宫、官禄宫等）
- 主星安星算法

---

## English

**tianji** is a pure-Python library for Chinese metaphysics calculations.

### Features

- **BaZi (Eight Characters)**: Four-pillar chart, Ten Gods, Five Elements, Luck Pillars
- **Liu Yao (Six Lines)**: 64 hexagrams, divination casting, full analysis
- **Zi Wei Dou Shu (Purple Star Astrology)**: 12-palace chart, star placement
- **LLM Layer**: Optional OpenAI integration for interpretation
- **REST API**: FastAPI-powered endpoints
- **CLI**: Command-line interface

### Installation

```bash
pip install tianji
pip install "tianji[llm]"  # with OpenAI support
```

### Quick Example

```python
from datetime import datetime
from tianji.bazi import BaZiChart

chart = BaZiChart(birth_dt=datetime(1990, 5, 15, 14, 30), gender="male")
print(chart.year_pillar)   # 庚午
print(chart.month_pillar)  # 辛巳
print(chart.day_pillar)    # 丙申
print(chart.hour_pillar)   # 甲未
```

---

## 项目结构

```
tianji/
├── src/tianji/
│   ├── calendar/     # 干支历法引擎
│   ├── bazi/         # 八字算法
│   ├── liuyao/       # 六爻算法
│   ├── ziwei/        # 紫微斗数
│   ├── llm/          # LLM 解读层
│   └── api/          # FastAPI 接口
├── tests/
├── examples/
└── pyproject.toml
```

---

## 贡献

欢迎提交 Issue 和 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License — Copyright (c) 2026 Zijian Ni
