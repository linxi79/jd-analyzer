"""命令行入口：解析参数、读文件、读环境变量、调用 core、打印结果。

进度/错误信息走 stderr，分析结果走 stdout——这样可以 `jd-analyzer > out.md`
把纯结果重定向到文件，提示语不会混进去。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import __version__
from .core import DEFAULT_MODEL, analyze, create_client


def read_jd(path: Path) -> str:
    """读取并校验 JD 文件，返回去掉首尾空白的文本。"""
    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"{path} 是空的。")
    return text


def main(argv: list[str] | None = None) -> int:
    """程序主入口，返回进程退出码（0 成功，非 0 失败）。"""
    parser = argparse.ArgumentParser(
        prog="jd-analyzer",
        description="读取招聘 JD，用大模型分析候选人匹配度。",
    )
    parser.add_argument(
        "jd_file",
        nargs="?",
        default="jd.txt",
        help="JD 文本文件路径（默认：当前目录的 jd.txt）",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型名（默认 {DEFAULT_MODEL}）")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    # 从 .env 加载环境变量，再读密钥
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print(
            "错误：没读到 DEEPSEEK_API_KEY，请在 .env 里填好你的 DeepSeek 密钥。", file=sys.stderr
        )
        return 1

    try:
        jd_text = read_jd(Path(args.jd_file))
    except (FileNotFoundError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    client = create_client(api_key)
    print(f"正在用 {args.model} 分析 {args.jd_file} ...\n", file=sys.stderr)
    print(analyze(client, jd_text, model=args.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
