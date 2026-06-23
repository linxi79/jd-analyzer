# jd-analyzer

[![CI](https://github.com/linxi79/jd-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/linxi79/jd-analyzer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

读取招聘「职位描述(JD)」，用大模型分析候选人匹配度，输出四块结论的命令行工具。

- ① 硬性要求 —— JD 里真正卡人的门槛
- ② 候选人能满足哪些 —— 默认画像「5 年前端、近期转 AI 的工程师」
- ③ 可能缺哪些
- ④ 下一个最该补的一项 —— 只给一条最高优先级建议

底层用 [DeepSeek](https://platform.deepseek.com/)（OpenAI 兼容接口）。

## 快速开始

依赖管理用 [uv](https://docs.astral.sh/uv/)。没装先装：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

然后：

```bash
# 1. 安装依赖（自动建虚拟环境、按 uv.lock 锁定版本）
uv sync

# 2. 配密钥：复制模板，填入你的 DeepSeek key
cp .env.example .env
#   编辑 .env，填 DEEPSEEK_API_KEY=sk-...

# 3. 运行
uv run jd-analyzer            # 分析当前目录的 jd.txt
uv run jd-analyzer other.txt  # 分析指定文件
uv run jd-analyzer --help     # 查看所有参数
```

> 密钥从环境变量 `DEEPSEEK_API_KEY` 读取（通过 `.env` + python-dotenv 加载）。
> `.env` 已被 git 忽略，不会提交。

## 开发

```bash
uv sync --dev          # 装上开发依赖（ruff / mypy / pytest）

uv run ruff format .   # 自动格式化
uv run ruff check .    # 代码检查（lint）
uv run mypy            # 静态类型检查
uv run pytest          # 跑测试
```

CI（GitHub Actions）会在每次 push / PR 自动跑以上全部检查，见 `.github/workflows/ci.yml`。

## 项目结构

```
jd_tools/
├── src/jd_analyzer/      # 包源码
│   ├── core.py           # 纯逻辑：构造 prompt、调用模型（可单测）
│   └── cli.py            # 命令行入口：参数 / 文件 / 环境变量 / 打印
├── tests/                # pytest 测试（mock 掉真实 API）
├── .github/workflows/    # CI
├── pyproject.toml        # 项目元数据 + 依赖 + ruff/mypy/pytest 配置
├── uv.lock               # 锁定的精确依赖版本（保证可复现）
├── jd.txt                # 示例 JD
├── .env.example          # 密钥模板（.env 本身不提交）
└── LICENSE               # MIT
```

`core.py` 与 `cli.py` 分离是刻意的：核心逻辑不碰文件和网络，可以被测试直接调用。

## 许可

[MIT](LICENSE)
