"""Consulting framework matching and structured analysis."""

from dataclasses import dataclass

from .knowledge import Chunk


@dataclass
class AnalysisResult:
    """Structured analysis output."""

    question: str
    frameworks_used: list[str]
    analysis_path: list[str]
    retrieved_context: list[Chunk]
    recommendation: str
    verbose: bool = False


# Question type to framework mapping
FRAMEWORK_HINTS = {
    "行业": ["波特五力模型", "PEST/PESTEL 分析"],
    "竞争": ["波特五力模型", "3C 模型"],
    "战略": ["3C 模型", "安索夫矩阵", "SWOT 分析", "战略屋", "Playing to Win"],
    "增长": ["增长飞轮", "安索夫矩阵", "BCG 矩阵", "麦肯锡三层面增长模型"],
    "利润": ["MECE 原则", "价值链分析"],
    "成本": ["MECE 原则", "价值链分析", "行业成本曲线"],
    "业务": ["BCG 矩阵", "商业画布", "GE-麦肯锡矩阵"],
    "产品": ["安索夫矩阵", "商业画布"],
    "市场": ["安索夫矩阵", "波特五力模型", "SWOT 分析", "Go-To-Market 战略框架"],
    "优势": ["SWOT 分析", "价值链分析"],
    "劣势": ["SWOT 分析"],
    "机会": ["SWOT 分析", "PEST/PESTEL 分析"],
    "威胁": ["SWOT 分析", "PEST/PESTEL 分析"],
    "分析": ["MECE 原则", "问题解决七步法"],
    "汇报": ["金字塔原理"],
    "报告": ["金字塔原理"],
    "方案": ["金字塔原理", "问题解决七步法"],
    "拆解": ["MECE 原则", "问题解决七步法"],
    "商业模式": ["商业画布"],
    "创业": ["商业画布", "SWOT 分析"],
    "投资": ["波特五力模型", "BCG 矩阵", "GE-麦肯锡矩阵"],
    "组合": ["BCG 矩阵", "GE-麦肯锡矩阵"],
    "宏观": ["PEST/PESTEL 分析"],
    "政策": ["PEST/PESTEL 分析"],
    "环境": ["PEST/PESTEL 分析"],
    "客户": ["3C 模型", "商业画布", "消费者决策旅程"],
    "价值": ["价值链分析", "商业画布"],
    "流程": ["价值链分析", "PDCA 循环"],
    "组织": ["问题解决七步法", "MECE 原则", "麦肯锡 7S 框架"],
    "规划": ["战略金字塔", "战略屋", "平衡计分卡"],
    "愿景": ["战略屋", "战略金字塔", "Playing to Win"],
    "使命": ["战略屋", "战略金字塔"],
    "五年": ["战略金字塔", "战略屋", "麦肯锡三层面增长模型"],
    "长期": ["麦肯锡三层面增长模型", "未来倒推战略"],
    "短期": ["麦肯锡三层面增长模型", "PDCA 循环"],
    "创新": ["麦肯锡三层面增长模型", "未来倒推战略"],
    "转型": ["未来倒推战略", "影响力模型", "战略屋"],
    "变革": ["影响力模型", "麦肯锡 7S 框架"],
    "文化": ["麦肯锡 7S 框架", "影响力模型"],
    "人才": ["麦肯锡 7S 框架"],
    "领导": ["影响力模型", "麦肯锡 7S 框架"],
    "执行": ["PDCA 循环", "平衡计分卡", "战略路线图"],
    "落地": ["PDCA 循环", "战略路线图", "影响力模型"],
    "衡量": ["平衡计分卡", "战略画布"],
    "指标": ["平衡计分卡", "战略画布"],
    "KPI": ["平衡计分卡", "战略画布"],
    "上市": ["Go-To-Market 战略框架"],
    "发布": ["Go-To-Market 战略框架"],
    "GTM": ["Go-To-Market 战略框架"],
    "决策": ["决策树", "Playing to Win"],
    "收购": ["GE-麦肯锡矩阵", "战略控制地图"],
    "并购": ["GE-麦肯锡矩阵", "战略控制地图"],
    "消费者": ["消费者决策旅程"],
    "购买": ["消费者决策旅程"],
    "用户": ["消费者决策旅程", "3C 模型"],
}


def match_frameworks(question: str, retrieved_chunks: list[Chunk]) -> list[str]:
    """Determine which frameworks to use based on question and retrieved context."""
    candidates = {}

    for keyword, frameworks in FRAMEWORK_HINTS.items():
        if keyword in question:
            for fw in frameworks:
                candidates[fw] = candidates.get(fw, 0) + 0.5

    for chunk in retrieved_chunks:
        fw = chunk.framework_name
        candidates[fw] = candidates.get(fw, 0) + chunk.score

    sorted_fws = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    result = [fw for fw, score in sorted_fws if score > 0.1]
    return result[:3] if result else ["MECE 原则", "问题解决七步法"]


def build_analysis_prompt(
    question: str,
    frameworks: list[str],
    context_chunks: list[Chunk],
) -> str:
    """Build the LLM prompt for structured analysis."""

    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"\n--- 知识片段 {i} ({chunk.framework_name}) ---\n"
        context_text += chunk.text + "\n"

    frameworks_str = "\n".join(f"- {fw}" for fw in frameworks)

    prompt = (
        "你是资深管理咨询顾问。基于以下知识库，用咨询框架对问题做完整分析。\n"
        "要求：直接输出报告，不要引导语；结合问题展开每个框架；建议要具体可执行；必须写完所有章节。\n\n"
        f"## 问题\n{question}\n\n"
        f"## 推荐框架\n{frameworks_str}\n\n"
        f"## 知识库\n{context_text}\n\n"
        "## 输出格式\n\n"
        "### 一、问题界定\n一句话定义核心问题。\n\n"
        "### 二、框架分析\n对每个框架结合问题具体分析，说明应用逻辑和初步判断。\n\n"
        "### 三、MECE结构化拆解\n用树状结构层次化拆解问题。\n\n"
        "### 四、关键发现与建议\n核心发现2-3条、具体建议（可执行行动项）、风险提示。\n\n"
        "### 五、下一步行动\n需要进一步收集的数据或信息。\n"
    )
    return prompt
