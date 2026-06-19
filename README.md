# Consulting RAG Agent - 管理咨询知识问答系统

基于 RAG (检索增强生成) 的管理咨询框架分析 Agent。输入行业问题，自动匹配咨询框架，输出结构化分析路径和建议。

## 功能

- 内置 36 个经典咨询框架知识库 (MECE、波特五力、SWOT、BCG 矩阵、战略屋、Playing to Win 等)
- TF-IDF + 中文分词的语义检索
- 基于关键词 + 语义相似度的框架自动匹配
- 支持 OpenAI 兼容 API (OpenAI / DeepSeek / 通义千问等)
- 无 API Key 时自动降级为模板模式
- **默认仅输出分析结果**，`--verbose` 模式显示分析链详情

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 模板模式 (无需 API Key)
python main.py "一家传统制造企业想进入新能源汽车行业，如何分析这个战略决策?"

# 详细模式 (显示分析链)
python main.py --verbose "如何分析中国新能源汽车行业的竞争格局?"

# 配置 LLM 后获得完整分析
export LLM_API_KEY="your-api-key"
export LLM_BASE_URL="https://api.deepseek.com/v1"  # 可选
export LLM_MODEL="deepseek-chat"                     # 可选
python main.py "如何分析中国新能源汽车行业的竞争格局?"
```

## 命令行选项

```
python main.py "问题"              # 默认模式，仅输出分析结果
python main.py --verbose "问题"    # 详细模式，显示分析链
python main.py -v "问题"           # 同上
```

## 交互模式

```bash
python main.py
# 输入问题即可获得分析
# 输入 'frameworks' 查看可用框架
# 输入 'verbose on' 开启详细模式
# 输入 'verbose off' 关闭详细模式
# 输入 'quit' 退出
```

## 项目结构

```
consulting-rag-agent/
├── main.py                              # 入口文件
├── requirements.txt
├── knowledge_base/                      # 咨询框架知识库
│   ├── consulting_frameworks.md         # 基础框架 (12个)
│   ├── mckinsey_frameworks.md           # 麦肯锡经典框架 (6个)
│   ├── strategy_planning_frameworks.md  # 战略规划框架 (4个)
│   ├── growth_innovation_frameworks.md  # 增长创新框架 (7个)
│   └── decision_execution_frameworks.md # 决策执行框架 (7个)
└── src/
    ├── config.py                        # 配置
    ├── knowledge.py                     # RAG 检索引擎
    ├── frameworks.py                    # 框架匹配与 Prompt 构建
    └── agent.py                         # Agent 主逻辑
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_API_KEY` | LLM API 密钥 | (空) |
| `LLM_BASE_URL` | API 地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | 生成温度 | `0.3` |
| `TOP_K_RETRIEVAL` | 检索数量 | `3` |

## 内置框架 (36个)

**基础框架**: MECE 原则、波特五力、SWOT、3C 模型、价值链分析、BCG 矩阵、安索夫矩阵、麦肯锡七步法、金字塔原理、商业画布、增长飞轮、PEST/PESTEL

**麦肯锡系列**: GE-麦肯锡矩阵、7S 框架、业务系统框架、行业成本曲线、SCP 框架、战略控制地图

**战略规划**: 三层面增长模型 (3 Horizons)、战略金字塔、战略屋 (Strategy House)、Playing to Win

**增长创新**: 赢增长矩阵、GTM 战略框架、战略路线图、平衡计分卡、未来倒推战略、战略画布

**决策执行**: 决策树、PDCA 循环、影响力模型、消费者决策旅程

## 扩展知识库

往 `knowledge_base/` 目录添加 `.md` 文件即可扩展知识库，格式参考现有文件。系统启动时会自动扫描目录下所有 `.md` 文件，按 `##` 分节后建立索引。

## 升级到 LLM 模式

模板模式仅展示框架定义，配置 LLM API 后可获得：
- 结合具体问题的框架应用分析
- MECE 原则的结构化拆解
- 可执行的具体建议和风险提示
