#!/usr/bin/env python3
"""
Consulting RAG Agent - 管理咨询知识问答系统

Usage:
    python main.py                        # Interactive mode
    python main.py "你的问题"              # Single question mode

Environment Variables:
    LLM_API_KEY      API key for LLM (OpenAI-compatible)
    LLM_BASE_URL     API endpoint (default: https://api.openai.com/v1)
    LLM_MODEL        Model name (default: gpt-4o-mini)
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
╚══════════════════════════════════════════════════════╝
"""


def format_result(result):
    """Format analysis result for terminal output."""
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


def main():
    """Main entry point."""
    config = Config()
    agent = ConsultingAgent(config)

    # Check if LLM is configured
    has_llm = bool(config.LLM_API_KEY)
    if not has_llm:
        print("\n[提示] 未配置 LLM_API_KEY，将使用模板模式输出。")
        print("  设置环境变量以启用完整 LLM 分析:")
        print("  export LLM_API_KEY='your-api-key'")
        print("  export LLM_BASE_URL='https://api.openai.com/v1'  # 可选")
        print("  export LLM_MODEL='gpt-4o-mini'                   # 可选\n")

    # Single question mode
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        if question in ("--help", "-h"):
            print(__doc__)
            return
        result = agent.analyze(question)
        format_result(result)
        return

    # Interactive mode
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

        result = agent.analyze(question)
        format_result(result)


if __name__ == "__main__":
    main()
