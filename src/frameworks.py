"""Consulting framework matching and structured analysis."""

from dataclasses import dataclass
from typing import List, Optional

from .knowledge import Chunk


@dataclass
class AnalysisResult:
    """Structured analysis output."""

    question: str
    frameworks_used: List[str]
    analysis_path: List[str]
    retrieved_context: List[Chunk]
    recommendation: str


# Question type to framework mapping
FRAMEWORK_HINTS = {
    # Original frameworks
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
    "组织": ["麦肯锡7步法", "MECE 原则", "麦肯锡 7S 框架"],
    # New frameworks
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
    "人才": ["麦肯锡 7S 框架", "4C 招聘框架"],
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


def match_frameworks(question: str, retrieved_chunks: List[Chunk]) -> List[str]:
    """Determine which frameworks to use based on question and retrieved context."""
    candidates = {}

    # 1. Keyword-based hint matching
    for keyword, frameworks in FRAMEWORK_HINTS.items():
        if keyword in question:
            for fw in frameworks:
                candidates[fw] = candidates.get(fw, 0) + 0.5

    # 2. Boost based on retrieval scores
    for chunk in retrieved_chunks:
        fw = chunk.framework_name
        candidates[fw] = candidates.get(fw, 0) + chunk.score

    # Sort by score, return top matches
    sorted_fws = sorted(candidates.items(), key=lambda x: x[1], reverse=True)

    # Return frameworks with meaningful scores
    result = [fw for fw, score in sorted_fws if score > 0.1]
    return result[:3] if result else ["MECE 原则", "问题解决七步法"]


def build_analysis_prompt(
    question: str,
    frameworks: List[str],
    context_chunks: List[Chunk],
) -> str:
    """Build the LLM prompt for structured analysis."""

    # Format retrieved context
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"\n--- 知识片段 {i} (来源: {chunk.framework_name}) ---\n"
        context_text += chunk.text + "\n"

    frameworks_str = "、".join(frameworks)

    prompt = f"""你是一位资深管理咨询顾问。请基于以下知识库内容，使用咨询框架对问题进行结构化拆解和分析。

## 用户问题
{question}

## 推荐使用的咨询框架
{frameworks_str}

## 知识库参考内容
{context_text}

## 输出要求

请按以下格式输出结构化分析:

### 一、问题界定
用一句话清晰定义核心问题。

### 二、分析路径
使用推荐的咨询框架，逐步拆解问题:
- 每个框架的应用逻辑
- 关键维度和分析要素
- 框架之间的关联

### 三、结构化拆解
用MECE原则对问题进行层次化拆解，展示为树状结构。

### 四、关键发现与建议
基于框架分析得出:
- 核心发现 (2-3条)
- 具体建议 (可执行的行动项)
- 风险提示

### 五、下一步行动
建议进一步收集哪些数据或信息来深化分析。
"""
    return prompt
