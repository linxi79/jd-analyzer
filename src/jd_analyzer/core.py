"""核心逻辑：构造 prompt、调用大模型。

刻意和「命令行解析 / 文件读写 / 环境变量」解耦——这样这些纯函数可以被
单元测试直接调用、用假的客户端 mock 掉真实 API，不花钱也不依赖网络。
"""

from __future__ import annotations

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# DeepSeek 用 OpenAI 兼容接口。模型名以官方文档为准：
# v4-pro 强（适合分析），v4-flash 快而省。旧的 deepseek-chat/-reasoner 于 2026-07-24 弃用。
DEFAULT_MODEL = "deepseek-v4-pro"
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_CANDIDATE = "一个有 5 年前端开发经验、最近转向 AI 方向的工程师"

SYSTEM_PROMPT = "你是一位资深的技术招聘顾问。"

PROMPT_TEMPLATE = """下面是一份招聘 JD，请针对「{candidate}」做分析。

严格按以下四个小标题输出，每块用简洁的中文要点（bullet）：

① 硬性要求
   —— 从 JD 中提炼出真正卡人的硬门槛（不是加分项）。

② 这位候选人大概能满足哪些
   —— 基于他的背景，逐条说明能对上的要求。

③ 可能缺哪些
   —— 他大概率不具备或较弱的点。

④ 下一个最该补的一项
   —— 只给一条、最高优先级的建议，并说明为什么是它。

JD 原文：
---
{jd}
---"""


def build_prompt(jd_text: str, candidate: str = DEFAULT_CANDIDATE) -> str:
    """把 JD 文本和候选人画像填进模板，返回完整的用户提示词。"""
    return PROMPT_TEMPLATE.format(candidate=candidate, jd=jd_text.strip())


def create_client(api_key: str, base_url: str = DEFAULT_BASE_URL) -> OpenAI:
    """创建 DeepSeek（OpenAI 兼容）客户端。"""
    return OpenAI(api_key=api_key, base_url=base_url)


def analyze(
    client: OpenAI,
    jd_text: str,
    *,
    candidate: str = DEFAULT_CANDIDATE,
    model: str = DEFAULT_MODEL,
) -> str:
    """调用大模型分析一份 JD，返回结论正文。"""
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(jd_text, candidate)},
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content or ""
