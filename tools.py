"""Narrow read-only and append-only tools used by the profile workflow."""

import fcntl
import json
import re
from datetime import datetime, timezone
from typing import Literal

from langchain_core.tools import tool

from config import KNOWLEDGE_PATH, LOG_DIR, LOG_PATHS


@tool
def read_knowledge_base(query: str) -> str:
    """Read relevant sections from the fixed, read-only profile knowledge file."""
    if not KNOWLEDGE_PATH.is_file():
        raise FileNotFoundError("The profile knowledge file is unavailable")

    content = KNOWLEDGE_PATH.read_text(encoding="utf-8")
    sections: list[str] = []
    current: list[str] = []
    for line in content.splitlines():
        if line.startswith("## ") and current:
            sections.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current).strip())

    query_terms = {
        term for term in re.findall(r"[a-z0-9+#.-]+", query.lower()) if len(term) > 2
    }
    ranked = sorted(
        enumerate(sections),
        key=lambda item: sum(
            1 for term in query_terms if term in item[1].lower()
        ),
        reverse=True,
    )
    matching = [
        section
        for _, section in ranked[:5]
        if any(term in section.lower() for term in query_terms)
    ]
    selected = "\n\n".join(matching) if matching else content
    return selected[:24000]


def _append_record(
    log_name: Literal["unrelated", "discussion", "contact", "error"],
    record: dict[str, object],
) -> int:
    """Append one JSONL record under a process-safe lock; paths are never inputs."""
    path = LOG_PATHS[log_name]
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOG_DIR / ".write.lock"

    with lock_path.open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        sequence = 0
        if path.exists():
            with path.open("r", encoding="utf-8") as existing:
                for line in existing:
                    try:
                        sequence = max(sequence, int(json.loads(line)["sequence_number"]))
                    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                        continue

        sequence += 1
        entry = {
            "sequence_number": sequence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        with path.open("a", encoding="utf-8") as output:
            output.write(json.dumps(entry, ensure_ascii=False) + "\n")
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    return sequence


@tool
def append_unrelated_question_log(user_question: str, classification_reason: str) -> str:
    """Append an out-of-scope question and its classification reason."""
    sequence = _append_record(
        "unrelated",
        {
            "user_question": user_question,
            "classification_reason": classification_reason,
        },
    )
    return f"Recorded unrelated question {sequence}."


@tool
def append_discussion_log(user_question: str, assistant_response: str) -> str:
    """Append one relevant profile question and its response."""
    sequence = _append_record(
        "discussion",
        {"user_question": user_question, "assistant_response": assistant_response},
    )
    return f"Recorded discussion {sequence}."


@tool
def append_contact_log(
    email: str | None, phone: str | None, associated_user_message: str
) -> str:
    """Append contact details voluntarily shared in the current user message."""
    sequence = _append_record(
        "contact",
        {
            "email": email,
            "phone": phone,
            "associated_user_message": associated_user_message,
        },
    )
    return f"Recorded contact details {sequence}."


@tool
def append_error_log(error_category: str, safe_diagnostic_details: str) -> str:
    """Append a safe error category and diagnostic without stack traces or secrets."""
    sequence = _append_record(
        "error",
        {
            "error_category": error_category,
            "safe_diagnostic_details": safe_diagnostic_details,
        },
    )
    return f"Recorded application error {sequence}."


def extract_contact_details(message: str) -> tuple[str | None, str | None]:
    """Return an email and/or plausible phone number found in a message."""
    email_match = re.search(
        r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?![\w.-])", message
    )
    phone = None
    for match in re.finditer(r"(?<!\w)\+?\d[\d(). -]{6,}\d(?!\w)", message):
        candidate = match.group().strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate):
            continue
        if 8 <= len(re.sub(r"\D", "", candidate)) <= 15:
            phone = candidate
            break
    return (email_match.group() if email_match else None, phone)