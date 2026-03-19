# Contributing to tianji (天机)

[English](#english) | [中文](#中文)

---

## English

Thank you for your interest in contributing to **tianji**! This library aims to provide accurate, well-documented implementations of Chinese metaphysical systems.

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/tianji.git`
3. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
4. Install dev dependencies: `pip install -e ".[dev]"`
5. Create a branch: `git checkout -b feature/your-feature-name`

### Development Setup

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Docstrings in Chinese + English where applicable
- Run `ruff check .` and `ruff format .` before committing

### Submitting a PR

1. Write or update tests for your changes
2. Ensure all tests pass: `pytest`
3. Update CHANGELOG.md
4. Open a Pull Request with a clear description

### Algorithm Accuracy

For metaphysical algorithms (BaZi, Liu Yao, Zi Wei), please cite classical sources or reference texts when introducing new logic. Accuracy matters more than cleverness.

---

## 中文

感谢您对 **天机** 库的贡献兴趣！本库致力于提供准确、文档完善的中国玄学算法实现。

### 快速开始

1. Fork 本仓库
2. 克隆您的 Fork: `git clone https://github.com/YOUR_USERNAME/tianji.git`
3. 创建虚拟环境: `python -m venv .venv && source .venv/bin/activate`
4. 安装开发依赖: `pip install -e ".[dev]"`
5. 创建分支: `git checkout -b feature/您的功能名称`

### 代码风格

- 遵循 PEP 8 规范
- 全面使用类型注解
- 注释和文档字符串建议中英双语
- 提交前运行 `ruff check .` 和 `ruff format .`

### 提交 PR

1. 为您的更改编写或更新测试
2. 确保所有测试通过: `pytest`
3. 更新 CHANGELOG.md
4. 开启 Pull Request，并提供清晰的说明

### 算法准确性

对于玄学算法（八字、六爻、紫微斗数），新增逻辑时请引用经典文献或参考资料。
准确性比代码技巧更重要。

### 常见贡献方向

- 🐛 修复算法错误
- 📚 添加更多节气/星盘算法
- 🌐 改进多语言支持
- ✅ 增加测试用例
- 📖 完善文档

我们欢迎所有对中国传统文化和技术感兴趣的贡献者！
