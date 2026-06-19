"""Main agent orchestrator for consulting RAG system."""

from typing import Optional

from .config import Config
from .knowledge import KnowledgeBase
from .frameworks import match_frameworks, build_analysis_prompt, AnalysisResult


class ConsultingAgent:
    """RAG-powered consulting analysis agent."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.kb = KnowledgeBase(self.config)
        self._llm_client = None

    @property
    def llm_client(self):
        """Lazy-init OpenAI-compatible client."""
        if self._llm_client is None:
            if not self.config.LLM_API_KEY:
                return None
            try:
                from openai import OpenAI

                self._llm_client = OpenAI(
                    api_key=self.config.LLM_API_KEY,
                    base_url=self.config.LLM_BASE_URL,
                )
            except ImportError:
                return None
        return self._llm_client

    def analyze(self, question: str) -> AnalysisResult:
        """Run full RAG analysis pipeline on a question."""

        # Step 1: Retrieve relevant knowledge chunks (semantic search)
        chunks = self.kb.retrieve(question, top_k=self.config.TOP_K_RETRIEVAL)

        # Step 2: Match frameworks
        frameworks = match_frameworks(question, chunks)

        # Step 2.5: Supplement with framework definitions if missing
        retrieved_names = {c.framework_name for c in chunks}
        for fw in frameworks:
            if fw not in retrieved_names:
                extra = self.kb.retrieve_by_framework(fw)
                if extra:
                    chunks.extend(extra[:1])

        # Step 3: Generate analysis path
        analysis_path = [
            f"检索到 {len(chunks)} 个相关知识片段",
            f"匹配咨询框架: {' -> '.join(frameworks)}",
        ]

        if chunks:
            top_chunk = chunks[0]
            analysis_path.append(
                f"最高相关度: {top_chunk.framework_name} (相似度: {top_chunk.score:.3f})"
            )

        # Step 4: Generate recommendation
        recommendation = self._generate(question, frameworks, chunks)

        return AnalysisResult(
            question=question,
            frameworks_used=frameworks,
            analysis_path=analysis_path,
            retrieved_context=chunks,
            recommendation=recommendation,
        )

    def _generate(
        self, question: str, frameworks: list, chunks: list
    ) -> str:
        """Generate analysis using LLM or template fallback."""
        client = self.llm_client
        prompt = build_analysis_prompt(question, frameworks, chunks)

        if client:
            return self._call_llm(client, prompt)
        else:
            return self._template_output(question, frameworks, chunks)

    def _call_llm(self, client, prompt: str) -> str:
        """Call OpenAI-compatible LLM API."""
        try:
            response = client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深管理咨询顾问，擅长使用咨询框架进行结构化分析。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=self.config.LLM_MAX_TOKENS,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[LLM 调用失败: {e}]\n\n" + self._template_output(
                question="", frameworks=[], chunks=[]
            )

    def _template_output(
        self, question: str, frameworks: list, chunks: list
    ) -> str:
        """Template-based output when no LLM is available."""
        # Build a lookup from framework name to chunk text
        chunk_map = {c.framework_name: c.text for c in chunks}

        lines = []
        lines.append("=" * 60)
        lines.append("管理咨询结构化分析报告 (模板模式)")
        lines.append("=" * 60)

        if question:
            lines.append(f"\n问题: {question}")

        lines.append(f"\n使用的框架: {', '.join(frameworks)}")

        # Analysis path with framework details
        lines.append("\n--- 分析路径 ---")
        for fw in frameworks:
            lines.append(f"\n  [{fw}]")
            # Try to get content from retrieved chunks first
            if fw in chunk_map:
                for line in chunk_map[fw].split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        lines.append(f"    {line}")
            else:
                # Find any chunk that contains the framework name
                for c in chunks:
                    if fw in c.framework_name or c.framework_name in fw:
                        for line in c.text.split("\n"):
                            line = line.strip()
                            if line and not line.startswith("#"):
                                lines.append(f"    {line}")
                        break

        # Structured recommendation
        lines.append("\n--- 结构化建议 ---")
        lines.append("1. 使用上述框架逐一分析问题的各个维度")
        lines.append("2. 用 MECE 原则确保分析不重叠、不遗漏")
        lines.append("3. 综合各框架结论，形成统一的战略建议")

        lines.append("\n--- 升级提示 ---")
        lines.append("配置 LLM_API_KEY 环境变量可获得完整 LLM 分析:")
        lines.append("  export LLM_API_KEY='your-api-key'")
        lines.append("  支持 OpenAI / DeepSeek / 通义千问等兼容 API")

        lines.append("\n--- 知识来源 ---")
        for i, c in enumerate(chunks, 1):
            lines.append(f"  [{i}] {c.framework_name} (相关度: {c.score:.3f})")

        return "\n".join(lines)
