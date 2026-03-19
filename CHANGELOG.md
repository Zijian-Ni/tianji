# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-19

### Added
- Initial release of tianji (天机) library
- BaZi (八字) four-pillar chart calculation
  - Year, month, day, hour pillar computation
  - 立春-based year boundary
  - 五虎遁月 month stem derivation
  - 五鼠遁时 hour stem derivation
  - 十神 (Ten Gods) calculation
  - 五行 (Five Elements) analysis
  - 日主强弱 (Day Master strength) judgment
  - 大运 (Luck Pillars) calculation
  - 刑冲合害 (Relationships) analysis
- Liu Yao (六爻) divination
  - 64 hexagram definitions with Unicode symbols
  - Time-based, number-based, and coin-flip casting methods
  - 装卦: 世应, 六亲, 六神, 动爻变爻 analysis
- Zi Wei Dou Shu (紫微斗数) basic framework
  - 12-palace chart
  - Major stars placement
- Calendar engine
  - 天干地支 (Heavenly Stems & Earthly Branches) tables
  - 六十甲子 cycle
  - 24节气 solar term calculation
  - Lunar calendar utilities via lunardate
- LLM interpretation layer (optional, requires OpenAI)
- FastAPI REST API
- CLI interface
- Comprehensive test suite

[Unreleased]: https://github.com/Zijian-Ni/tianji/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Zijian-Ni/tianji/releases/tag/v0.1.0
