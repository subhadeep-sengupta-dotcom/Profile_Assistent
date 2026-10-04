"""Application paths and environment-backed model configuration."""

import os
from pathlib import Path

from groq import Groq

ROOT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_PATH = ROOT_DIR / "data" / "Knowledge.md"
LOG_DIR = ROOT_DIR / "logs"
LOG_PATHS = {
    "unrelated": LOG_DIR / "unrelated_questions.jsonl",
    "discussion": LOG_DIR / "discussion_log.jsonl",
    "contact": LOG_DIR / "contact_log.jsonl",
    "error": LOG_DIR / "error_log.jsonl",
}

DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_MODEL = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)


def create_groq_client() -> Groq:
    """Create a Groq client without ever including credentials in diagnostics."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return Groq(api_key=api_key)