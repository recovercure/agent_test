"""Main agent orchestrator for consulting RAG system."""

from typing import Optional

from .config import Config
from .knowledge import KnowledgeBase, Chunk
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

    def analyze(self, question: str, verbose: bool = False) -> AnalysisResult:
        """Run full RAG analysis pipeline on a question.

        Args:
            question: The user's question.
            verbose: If True, include analysis chain details in output.
        """

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

        # Step 3: Build analysis path (for verbose mode)
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
        recommendation = self._generate(question, frameworks, chunks, verbose)

        return AnalysisResult(
            question=question,
            frameworks_used=frameworks,
            analysis_path=analysis_path,
            retrieved_context=chunks,
            recommendation=recommendation,
            verbose=verbose,
        )

    def _generate(
        self, question: str, frameworks: list, chunks: list, verbose: bool
    ) -> str:
        """Generate analysis using LLM or template fallback."""
        client = self.llm_client
        prompt = build_analysis_prompt(question, frameworks, chunks)

        if client:
            return self._call_llm(client, prompt, verbose)
        else:
            return self._template_output(question, frameworks, chunks, verbose)

    def _call_llm(self, client, prompt: str, verbose: bool) -> str:
        """Call OpenAI-compatible LLM API."""
        try:
            response = client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深管理咨询顾问，擅长使用咨询框架进行结构化分析。请直接输出完整的结构化分析报告，不要输出分析过程或框架匹配信息。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.LLM_TEMPERATURE,
                max_tokens=self.config.LLM_MAX_TOKENS,
            )
            result = response.choices[0].message.content

            if verbose:
                # Prepend analysis chain info in verbose mode
                chain_info = self._build_chain_info(frameworks=[], chunks=[])
                return chain_info + "\n\n" + result
            return result
        except Exception as e:
            return f"[LLM 调用失败: {e}]\n\n" + self._template_output(
                question="", frameworks=[], chunks=[], verbose=verbose
            )

    def _build_chain_info(self, frameworks: list, chunks: list) -> str:
        """Build analysis chain information for verbose mode."""
        lines = ["[分析链详情]"]

        if chunks:
            lines.append(f"  检索到 {len(chunks)} 个相关知识片段")
            for i, c in enumerate(chunks, 1):
                lines.append(f"  [{i}] {c.framework_name} (相关度: {c.score:.3f})")

        if frameworks:
            lines.append(f"  匹配框架: {' -> '.join(frameworks)}")

        return "\n".join(lines)

    def _template_output(
        self, question: str, frameworks: list, chunks: list, verbose: bool
    ) -> str:
        """Template-based output when no LLM is available."""
        # Build a lookup from framework name to chunk text
        chunk_map: dict[str, str] = {}
        for c in chunks:
            if c.framework_name not in chunk_map:
                chunk_map[c.framework_name] = c.text

        lines = []

        # In verbose mode, show the analysis chain
        if verbose:
            lines.append(self._build_chain_info(frameworks, chunks))
            lines.append("")

        # Main analysis output
        lines.append("=" * 60)
        lines.append("管理咨询结构化分析报告")
        lines.append("=" * 60)

        if question:
            lines.append(f"\n问题: {question}")

        lines.append(f"\n推荐框架: {', '.join(frameworks)}")

        # Framework analysis section
        lines.append("\n--- 框架分析 ---")
        for fw in frameworks:
            lines.append(f"\n  [{fw}]")
            # Try to get content from retrieved chunks
            content = chunk_map.get(fw)
            if not content:
                # Find any chunk that contains the framework name
                for c in chunks:
                    if fw in c.framework_name or c.framework_name in fw:
                        content = c.text
                        break

            if content:
                # Extract key points, skip headers
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        lines.append(f"    {line}")
            else:
                lines.append("    (未找到该框架的详细定义)")

        # Structured recommendation
        lines.append("\n--- 分析建议 ---")
        lines.append("1. 使用上述框架逐一分析问题的各个维度")
        lines.append("2. 用 MECE 原则确保分析不重叠、不遗漏")
        lines.append("3. 综合各框架结论，形成统一的战略建议")

        # Knowledge sources (only in verbose mode)
        if verbose:
            lines.append("\n--- 知识来源 ---")
            for i, c in enumerate(chunks, 1):
                lines.append(f"  [{i}] {c.framework_name} (相关度: {c.score:.3f})")

        lines.append("=" * 60)
        return "\n".join(lines)
