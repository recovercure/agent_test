# Consulting RAG Agent - 管理咨询知识问答系统

基于 RAG (检索增强生成) 的管理咨询框架分析 Agent。输入行业问题，自动匹配咨询框架，输出结构化分析路径和建议。

## 功能

- 内置 12 个经典咨询框架知识库 (MECE、波特五力、SWOT、BCG 矩阵等)
- TF-IDF + 中文分词的语义检索
- 基于关键词 + 语义相似度的框架自动匹配
- 支持 OpenAI 兼容 API (OpenAI / DeepSeek / 通义千问等)
- 无 API Key 时自动降级为模板模式

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 模板模式 (无需 API Key)
python main.py "一家传统制造企业想进入新能源汽车行业，如何分析这个战略决策?"

# 配置 LLM 后获得完整分析
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.deepseek.com/v1"  # 可选
export LLM_MODEL="deepseek-chat"                     # 可选
python main.py "如何分析中国新能源汽车行业的竞争格局?"
```

## 交互模式

```bash
python main.py
# 输入问题即可获得分析
# 输入 'frameworks' 查看可用框架
# 输入 'quit' 退出
```

## 项目结构

```
consulting-rag-agent/
├── main.py                    # 入口文件
├── requirements.txt
├── knowledge_base/
│   └── consulting_frameworks.md   # 咨询框架知识库
└── src/
    ├── config.py              # 配置
    ├── knowledge.py           # RAG 检索引擎
    ├── frameworks.py          # 框架匹配与分析
    └── agent.py               # Agent 主逻辑
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | LLM API 密钥 | (空) |
| `LLM_BASE_URL` | API 地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | 生成温度 | `0.3` |
| `TOP_K_RETRIEVAL` | 检索数量 | `3` |

## 内置框架

1. MECE 原则
2. 波特五力模型
3. SWOT 分析
4. 3C 模型
5. 价值链分析
6. BCG 矩阵
7. 安索夫矩阵
8. 问题解决七步法
9. 金字塔原理
10. 商业画布
11. 增长飞轮
12. PEST/PESTEL 分析

## 扩展

往 `knowledge_base/` 目录添加 `.md` 文件即可扩展知识库，格式参考 `consulting_frameworks.md`。
