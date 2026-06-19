#!/usr/bin/env python3
"""
Consulting RAG Agent - 管理咨询知识问答系统

Usage:
    python main.py "你的问题"              # 默认模式，仅输出分析结果
    python main.py --verbose "你的问题"    # 详细模式，显示分析链
    python main.py --setup                 # 配置 LLM API (只需一次)
    python main.py                         # 交互模式

Options:
    --verbose, -v    显示分析链详情 (框架匹配、检索结果等)
    --setup          交互式配置 LLM API，保存到 config.json
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.config import Config
from src.agent import ConsultingAgent


BANNER = """
╔══════════════════════════════════════════════════════╗
║       管理咨询 RAG 知识问答系统                       ║
║       Consulting Framework Analysis Agent            ║
╠══════════════════════════════════════════════════════╣
║  输入行业问题，自动使用咨询框架结构化拆解分析         ║
║  输入 'quit' 或 'exit' 退出                          ║
║  输入 'frameworks' 查看可用框架                       ║
║  输入 'verbose on/off' 切换详细模式                   ║
╚══════════════════════════════════════════════════════╝
"""


def setup_wizard():
    """Interactive setup wizard for LLM configuration."""
    print("\n" + "=" * 50)
    print("  LLM API 配置向导")
    print("=" * 50)
    print("\n配置将保存到 config.json，之后无需重复设置。\n")

    # Load existing config
    config = Config()

    # API Key
    print(f"当前 API Key: {'***' + config.LLM_API_KEY[-4:] if config.LLM_API_KEY else '(未设置)'}")
    api_key = input("输入新的 API Key (回车跳过): ").strip()

    # Base URL
    print(f"\n当前 API 地址: {config.LLM_BASE_URL}")
    print("  常见地址:")
    print("  - OpenAI:      https://api.openai.com/v1")
    print("  - DeepSeek:    https://api.deepseek.com/v1")
    print("  - 通义千问:    https://dashscope.aliyuncs.com/compatible-mode/v1")
    print("  - Moonshot:    https://api.moonshot.cn/v1")
    print("  - 智谱AI:      https://open.bigmodel.cn/api/paas/v4")
    base_url = input("输入 API 地址 (回车跳过): ").strip()

    # Model
    print(f"\n当前模型: {config.LLM_MODEL}")
    print("  常见模型:")
    print("  - OpenAI:    gpt-4o-mini / gpt-4o")
    print("  - DeepSeek:  deepseek-chat / deepseek-reasoner")
    print("  - 通义千问:  qwen-plus / qwen-turbo")
    print("  - Moonshot:  moonshot-v1-8k / moonshot-v1-32k")
    model = input("输入模型名称 (回车跳过): ").strip()

    # Apply changes
    if api_key:
        config.LLM_API_KEY = api_key
    if base_url:
        config.LLM_BASE_URL = base_url
    if model:
        config.LLM_MODEL = model

    config.save()

    print("\n" + "=" * 50)
    print("  配置已保存到 config.json")
    print("=" * 50)
    print(f"  API 地址: {config.LLM_BASE_URL}")
    print(f"  模型:     {config.LLM_MODEL}")
    print(f"  API Key:  {'***' + config.LLM_API_KEY[-4:] if config.LLM_API_KEY else '(未设置)'}")
    print("\n现在可以直接使用: python main.py \"你的问题\"")
    print()


def format_result(result):
    """Format analysis result for terminal output."""
    print(result.recommendation)


def format_result_verbose(result):
    """Format analysis result with full analysis chain."""
    print("\n" + "=" * 60)
    print(f"问题: {result.question}")
    print("=" * 60)

    print("\n[分析路径]")
    for step in result.analysis_path:
        print(f"  -> {step}")

    print(f"\n[匹配框架] {', '.join(result.frameworks_used)}")

    if result.retrieved_context:
        print(f"\n[检索到 {len(result.retrieved_context)} 个相关知识片段]")
        for i, chunk in enumerate(result.retrieved_context, 1):
            print(f"  [{i}] {chunk.framework_name} (相关度: {chunk.score:.3f})")

    print("\n" + "-" * 60)
    print("[结构化分析]")
    print("-" * 60)
    print(result.recommendation)
    print("=" * 60)


def parse_args(args):
    """Parse command line arguments."""
    verbose = False
    question_parts = []

    for arg in args:
        if arg in ("--verbose", "-v"):
            verbose = True
        elif arg == "--setup":
            setup_wizard()
            sys.exit(0)
        elif arg in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        else:
            question_parts.append(arg)

    return verbose, " ".join(question_parts)


def main():
    """Main entry point."""
    config = Config()
    agent = ConsultingAgent(config)

    # Parse arguments
    verbose, question = parse_args(sys.argv[1:])

    # Single question mode
    if question:
        result = agent.analyze(question, verbose=verbose)
        if verbose:
            format_result_verbose(result)
        else:
            format_result(result)
        return

    # Interactive mode
    # Show LLM status
    has_llm = bool(config.LLM_API_KEY)
    if has_llm:
        print(f"\n[LLM 已配置] {config.LLM_MODEL} @ {config.LLM_BASE_URL}")
    else:
        print("\n[提示] 未配置 LLM，当前为模板模式。运行 'python main.py --setup' 配置。")

    print(BANNER)

    while True:
        try:
            question = input("\n请输入您的问题: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("再见!")
            break
        if question.lower() == "frameworks":
            print("\n可用咨询框架:")
            for fw in agent.kb.list_frameworks():
                print(f"  - {fw}")
            continue
        if question.lower() == "verbose on":
            verbose = True
            print("[详细模式已开启]")
            continue
        if question.lower() == "verbose off":
            verbose = False
            print("[详细模式已关闭]")
            continue
        if question.lower() == "setup":
            setup_wizard()
            # Reload config after setup
            config = Config()
            agent = ConsultingAgent(config)
            continue

        result = agent.analyze(question, verbose=verbose)
        if verbose:
            format_result_verbose(result)
        else:
            format_result(result)


if __name__ == "__main__":
    main()
