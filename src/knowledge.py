"""RAG knowledge retrieval engine using TF-IDF."""

import os
import re
from dataclasses import dataclass, field
from typing import List

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import Config


@dataclass
class Chunk:
    """A knowledge chunk with metadata."""

    text: str
    source: str
    framework_name: str
    score: float = 0.0


class KnowledgeBase:
    """RAG knowledge base with TF-IDF retrieval."""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.chunks: List[Chunk] = []
        self.vectorizer: TfidfVectorizer = None
        self.tfidf_matrix = None
        self._load()

    def _load(self):
        """Load and chunk all markdown files from knowledge directory."""
        raw_chunks = []
        kb_dir = self.config.KNOWLEDGE_DIR

        for fname in os.listdir(kb_dir):
            if not fname.endswith(".md"):
                continue
            filepath = os.path.join(kb_dir, fname)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by H2 sections (## N. Framework Name)
            sections = re.split(r"\n(?=## \d+\.)", content)
            for section in sections:
                section = section.strip()
                if not section or section.startswith("# "):
                    continue

                # Extract framework name from header
                header_match = re.match(r"## \d+\.\s*(.+?)(?:\n|$)", section)
                fw_name = header_match.group(1).strip() if header_match else "Unknown"

                # Chunk the section
                for chunk_text in self._split_text(section):
                    raw_chunks.append(
                        Chunk(
                            text=chunk_text,
                            source=fname,
                            framework_name=fw_name,
                        )
                    )

        self.chunks = raw_chunks
        if raw_chunks:
            self._build_index()

    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        size = self.config.CHUNK_SIZE
        overlap = self.config.CHUNK_OVERLAP

        if len(text) <= size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            # Try to break at paragraph boundary
            if end < len(text):
                last_newline = chunk.rfind("\n\n")
                if last_newline > size * 0.3:
                    chunk = chunk[:last_newline]
                    end = start + last_newline
            chunks.append(chunk.strip())
            start = end - overlap
        return [c for c in chunks if c]

    def _tokenize(self, text: str) -> str:
        """Chinese-aware tokenization using jieba."""
        words = jieba.cut(text, cut_all=False)
        return " ".join(words)

    def _build_index(self):
        """Build TF-IDF index over all chunks."""
        corpus = [self._tokenize(c.text) for c in self.chunks]
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, top_k: int = None) -> List[Chunk]:
        """Retrieve top-k most relevant chunks for the query."""
        if not self.chunks or self.tfidf_matrix is None:
            return []

        top_k = top_k or self.config.TOP_K_RETRIEVAL
        query_vec = self.vectorizer.transform([self._tokenize(query)])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top-k indices (retrieve more to allow dedup by framework)
        candidate_k = min(top_k * 3, len(self.chunks))
        top_indices = scores.argsort()[-candidate_k:][::-1]

        # Deduplicate: keep at most 2 chunks per framework
        seen_fw: dict = {}
        results = []
        for idx in top_indices:
            if scores[idx] < self.config.RELEVANCE_THRESHOLD:
                continue
            fw = self.chunks[idx].framework_name
            if seen_fw.get(fw, 0) >= 2:
                continue
            seen_fw[fw] = seen_fw.get(fw, 0) + 1
            chunk = Chunk(
                text=self.chunks[idx].text,
                source=self.chunks[idx].source,
                framework_name=fw,
                score=float(scores[idx]),
            )
            results.append(chunk)
            if len(results) >= top_k:
                break

        return results

    def retrieve_by_framework(self, framework_name: str) -> List[Chunk]:
        """Retrieve all chunks for a specific framework by name."""
        return [
            Chunk(text=c.text, source=c.source,
                  framework_name=c.framework_name, score=1.0)
            for c in self.chunks
            if framework_name in c.framework_name
        ]

    def list_frameworks(self) -> List[str]:
        """List all available framework names."""
        seen = set()
        for c in self.chunks:
            seen.add(c.framework_name)
        return sorted(seen)
