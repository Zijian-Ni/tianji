# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-11-23

- 八字支持分钟级输入、交节前后对照、UTC+8 民用时及整岁起运。浏览器和 Python 使用同一份离线星历。
- 修正闰月、公历农历互换、设备夏令时导致的日柱偏差。日期范围、核对数据及临界节气见 README。
- 六爻修正六九动爻、爻序和先天报数，时间起卦使用农历年月日与时支。紫微修正时辰输入、宫序、五行局与主星安置。
- 重做桌面和手机排盘页，增加交节依据、农历生辰换算、浅深主题和可还原的六爻分享。旧版八字分享链接可继续打开。
- 修复 REST 应用入口、序列化与 Python 可选解读模块的数据接线。新增两端共用的回归样例。

## [0.3.0] - 2026-03-27

### Added
- **纳音五行** — 完整 60 甲子纳音表，每柱显示对应纳音
- **胎元推算** — 月柱天干进一位 + 月柱地支进三位
- **命宫推算** — 年支逆推至出生月，再从出生时辰顺推至卯位
- **神煞系统** — 天乙贵人、文昌贵人、驿马、桃花、华盖、将星、天德、月德、禄神、羊刃
- **格局分析** — 根据月令透干判断格局（正官格、七杀格、食神格等）
- **用神忌神** — 基于日主强弱自动推荐用神/忌神五行
- **农历日期显示** — 阳历/农历对照
- **五行力量条形图** — 百分比显示，旺/中/弱/缺状态标注
- **大运纳音** — 每步大运显示纳音五行
- **流年增强** — 增加十神和纳音显示

### Fixed
- **日柱计算错误** — 修正基准日：1900-01-01 = 甲戌（序号 10），而非甲子
- **时辰传参错误** — select 值 0-11 正确转换为时钟小时
- **bazi.js / calendar.js API 不兼容** — 重写 bazi.js 适配 calendar.js 对象接口
- **月柱精度** — 从硬编码近似日期改为 calendar.js 节气精确计算
- **README 示例日柱** — 1990-05-15 日柱从错误的庚午改为正确的庚辰

### Changed
- **统一计算引擎** — app.js 删除独立的八字计算代码，全部委托给 bazi.js + calendar.js
- CSS 新增纳音、胎元命宫、神煞、格局、用神等 UI 组件样式

## [0.2.0] - 2026-03-27

### Added
- Modern web frontend (pure HTML/CSS/JS, zero dependencies)
  - Chinese-style dark/light theme with cinnabar red and gold accents
  - Responsive design for mobile/tablet/desktop
  - Chinese/English bilingual UI
  - Interactive BaZi calculator with real-time updates
  - Five Elements radar chart (Canvas)
  - Luck Pillars timeline visualization
  - Liu Yao hexagram SVG visualization with casting methods
  - Zi Wei Dou Shu 12-palace grid display
  - Share via URL feature
- Flow Year (流年) calculation in BaZi module
- GitHub Pages deployment workflow
- Release workflow (tag-triggered)
- Privacy-first design: zero data collection, fully offline

### Changed
- Updated CI to test Python 3.10–3.13
- Enhanced README with web UI documentation and privacy section

### Security
- Added Content Security Policy headers
- No external resource loading (CDN-free)
- No cookies, no localStorage tracking
- No analytics or third-party requests

## [0.1.0] - 2026-03-19

### Added
- Initial release of tianji (天机) library
- BaZi (八字) four-pillar chart calculation
  - Year, month, day, hour pillar computation
  - 十神, 五行, 日主强弱, 大运, 刑冲合害
- Liu Yao (六爻) divination (64 hexagrams, 3 casting methods)
- Zi Wei Dou Shu (紫微斗数) basic framework
- Calendar engine (天干地支, 六十甲子, 24节气, 农历)
- LLM interpretation layer (optional)
- FastAPI REST API
- CLI interface
- Comprehensive test suite

[Unreleased]: https://github.com/Zijian-Ni/tianji/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Zijian-Ni/tianji/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Zijian-Ni/tianji/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Zijian-Ni/tianji/releases/tag/v0.1.0
