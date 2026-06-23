"""core 模块的单元测试。

重点：用 MagicMock 假冒 OpenAI 客户端，**不发起真实 API 调用**——
测试因此免费、离线、稳定，CI 里也能随便跑。
"""

from unittest.mock import MagicMock

from jd_analyzer.core import analyze, build_prompt


def test_build_prompt_includes_jd_and_candidate() -> None:
    prompt = build_prompt("需要 3 年 Python 经验", candidate="张三")
    assert "需要 3 年 Python 经验" in prompt
    assert "张三" in prompt


def test_build_prompt_strips_whitespace() -> None:
    # 首尾空白应被去掉
    assert "  hi  " not in build_prompt("  hi  ")


def test_analyze_returns_model_text_and_passes_params() -> None:
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="四块分析结果"))
    ]

    result = analyze(fake_client, "some jd", model="deepseek-v4-pro")

    assert result == "四块分析结果"
    fake_client.chat.completions.create.assert_called_once()
    kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "deepseek-v4-pro"
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][1]["role"] == "user"


def test_analyze_handles_empty_content() -> None:
    # 模型返回 None 时应安全地变成空字符串，而不是崩溃
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content=None))
    ]
    assert analyze(fake_client, "some jd") == ""
