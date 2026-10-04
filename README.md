# Subhadeep Profile Chatbot

A focused, session-scoped assistant for questions about Subhadeep's career,
professional profile, skills, projects, education, interests, and recruitment
contact. It uses Gradio, LangGraph, the official Groq Python SDK, and the local
Markdown profile in `data/Knowledge.md`.

## Architecture

Each submitted message runs through a LangGraph workflow:

1. `profile_relevance_agent` classifies the question using the current session's
   recent history. Unrelated questions are not answered and are appended to
   `logs/unrelated_questions.jsonl` before the graph ends.
2. `profile_response_agent` reads relevant sections from the fixed, read-only
   `data/Knowledge.md`, drafts a grounded answer, and appends the question and
   answer to `logs/discussion_log.jsonl`.
3. `contact_capture_agent` detects an email address and/or phone number in a
   relevant message and appends voluntarily shared details to
   `logs/contact_log.jsonl`.
4. `error_handler` records a safe error category and diagnostic in
   `logs/error_log.jsonl` and returns a friendly message. Stack traces, API
   secrets, and raw internal exceptions are not shown in the UI.

Log tools accept data fields only; filenames are fixed in code. Each JSONL
record has a per-file increasing sequence number and an ISO-8601 UTC timestamp.
Writers are serialized, and existing records are never rewritten. Logs are
local application data and are not exposed in the public UI.

## Local Setup

Use Python 3.10 to 3.13. Python 3.14 currently emits an upstream LangChain/Pydantic compatibility warning.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Set the Groq key in your shell. The key is read only from `GROQ_API_KEY`; do not
put it in source code or profile files.

```bash
export GROQ_API_KEY="your-groq-api-key"
# Optional; default: openai/gpt-oss-120b
export GROQ_MODEL="openai/gpt-oss-120b"
python app.py
```

The app listens on `http://localhost:7860` and uses the official Groq Python SDK.

## Profile Knowledge

`data/Knowledge.md` is the only factual source used for answers. It is seeded
from the existing workspace `Knowledge.md` so the assistant has profile facts
on first launch. Review it for accuracy and paste or edit resume/profile details
there. Remove anything that should not be shared publicly. When a detail is
absent, the assistant is instructed to say it is not currently listed rather
than infer or invent it.

## Session Memory and Privacy

Conversation history is held in Gradio `gr.State` and exists only for the active
browser session. It is not stored as cross-user memory. Clear chat removes both
the displayed conversation and that session's in-memory history. Relevant
conversations and unrelated questions are separately logged on the server.

Contact details voluntarily included in a relevant message may be saved in
`logs/contact_log.jsonl` so Subhadeep can follow up. The assistant does not claim
that Subhadeep has contacted anyone. Treat the logs as personal data: restrict
server access and retention, and do not publish or commit them. The repository
ignores runtime JSONL logs by default.

## Hugging Face Spaces

1. Create a new Space and select the Gradio SDK.
2. Upload or push this project, including `app.py`, the Python modules,
   `requirements.txt`, and `data/Knowledge.md`. Do not upload `.env`, API-key
   files, or runtime logs.
3. In the Space, open **Settings > Variables and secrets** and add
   `GROQ_API_KEY` as a **Secret**. Optionally add `GROQ_MODEL` as a variable.
4. The Space installs `requirements.txt` and starts `python app.py`; the app
   binds to `0.0.0.0` and uses the platform-provided `PORT` (default 7860).
5. If the Space filesystem is ephemeral, logs may be lost when the Space
   restarts. Persistent storage is required if logs must survive restarts.

## Limitations and Grounding

The scope classifier and response writer are LLM calls, so classification and
wording are not mathematically guaranteed. The graph independently routes
out-of-scope requests to a fixed refusal, and response prompts restrict factual
claims to retrieved Markdown content. Keep `data/Knowledge.md` accurate, review
answers before relying on them for hiring decisions, and avoid adding sensitive
personal information. The application does not verify a person's identity,
send email, or guarantee delivery of saved contact details.