"""Configuration for Consulting RAG Agent."""

import os
import json


# Config file path (project root)
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config_file() -> dict:
    """Load saved config from config.json."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config_file(data: dict):
    """Save config to config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class Config:
    """Agent configuration. Priority: env vars > config.json > defaults."""

    def __init__(self):
        file_cfg = load_config_file()

        # LLM settings (OpenAI-compatible API)
        self.LLM_API_KEY = os.getenv("LLM_API_KEY") or file_cfg.get("llm_api_key", "")
        self.LLM_BASE_URL = os.getenv("LLM_BASE_URL") or file_cfg.get("llm_base_url", "https://api.openai.com/v1")
        self.LLM_MODEL = os.getenv("LLM_MODEL") or file_cfg.get("llm_model", "gpt-4o-mini")
        self.LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE") or file_cfg.get("llm_temperature", 0.3))
        self.LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS") or file_cfg.get("llm_max_tokens", 2000))

        # RAG settings
        self.KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR") or file_cfg.get(
            "knowledge_dir",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base"),
        )
        self.TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL") or file_cfg.get("top_k_retrieval", 3))
        self.CHUNK_SIZE = int(os.getenv("CHUNK_SIZE") or file_cfg.get("chunk_size", 500))
        self.CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP") or file_cfg.get("chunk_overlap", 50))

        # Framework matching
        self.RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD") or file_cfg.get("relevance_threshold", 0.15))

    def save(self):
        """Save current config to file."""
        data = {
            "llm_api_key": self.LLM_API_KEY,
            "llm_base_url": self.LLM_BASE_URL,
            "llm_model": self.LLM_MODEL,
            "llm_temperature": self.LLM_TEMPERATURE,
            "llm_max_tokens": self.LLM_MAX_TOKENS,
            "top_k_retrieval": self.TOP_K_RETRIEVAL,
            "chunk_size": self.CHUNK_SIZE,
            "chunk_overlap": self.CHUNK_OVERLAP,
            "relevance_threshold": self.RELEVANCE_THRESHOLD,
        }
        save_config_file(data)
