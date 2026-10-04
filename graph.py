"""LangGraph workflow for scope checking, grounded answers, and contact capture."""

from typing import TypedDict

from agents import classify_profile_question, draft_profile_response
from tools import (
    append_contact_log,
    append_discussion_log,
    append_error_log,
    append_unrelated_question_log,
    extract_contact_details,
    read_knowledge_base,
)


class ProfileState(TypedDict, total=False):
    question: str
    history: list[dict[str, str]]
    relevant: bool
    classification_reason: str
    answer: str
    error_category: str
    safe_diagnostic_details: str


def _safe_error(exc: Exception) -> tuple[str, str]:
    category = type(exc).__name__[:80]
    details = "Request could not be completed; internal error details were withheld."
    if isinstance(exc, RuntimeError) and str(exc) == "GROQ_API_KEY is not configured":
        details = "GROQ_API_KEY is not configured in the application environment."
        category = "ConfigurationError"
    return category, details


def _friendly_error(category: str) -> str:
    if category == "ConfigurationError":
        return (
            "The assistant is not configured yet. Set GROQ_API_KEY in the "
            "environment, restart the app, and try again."
        )
    return "Sorry, I couldn't complete that just now. Please try again in a moment."


def _capture_node_errors(node):
    def wrapped(state: ProfileState) -> ProfileState:
        try:
            return node(state)
        except Exception as exc:  # noqa: BLE001 - graph nodes must route unexpected failures
            category, details = _safe_error(exc)
            return {"error_category": category, "safe_diagnostic_details": details}

    return wrapped


def profile_relevance_agent(state: ProfileState) -> ProfileState:
    relevant, reason = classify_profile_question(
        state["question"], state.get("history", [])
    )
    if not relevant:
        append_unrelated_question_log.invoke(
            {"user_question": state["question"], "classification_reason": reason}
        )
        return {
            "relevant": False,
            "classification_reason": reason,
            "answer": "Thanks for your question. This chat is intended only for questions related to Subhadeep's profile, career, skills, projects, education, and professional interests.",
        }
    return {"relevant": True, "classification_reason": reason}


def profile_response_agent(state: ProfileState) -> ProfileState:
    recent = state.get("history", [])[-12:]
    context_query = "\n".join(
        [message.get("content", "") for message in recent]
        + [state["question"]]
    )
    knowledge = read_knowledge_base.invoke({"query": context_query})
    answer = draft_profile_response(state["question"], recent, knowledge)
    append_discussion_log.invoke(
        {"user_question": state["question"], "assistant_response": answer}
    )
    return {"answer": answer}


def contact_capture_agent(state: ProfileState) -> ProfileState:
    email, phone = extract_contact_details(state["question"])
    if email or phone:
        append_contact_log.invoke(
            {
                "email": email,
                "phone": phone,
                "associated_user_message": state["question"],
            }
        )
    return {}


def error_handler(state: ProfileState) -> ProfileState:
    try:
        append_error_log.invoke(
            {
                "error_category": state.get("error_category", "UnexpectedError"),
                "safe_diagnostic_details": state.get(
                    "safe_diagnostic_details", "Internal error details were withheld."
                ),
            }
        )
    except Exception:  # noqa: BLE001 - never leak a secondary logging failure
        return {
            "answer": _friendly_error(state.get("error_category", "UnexpectedError"))
        }
    return {"answer": _friendly_error(state.get("error_category", "UnexpectedError"))}


def _route_after_relevance(state: ProfileState) -> str:
    if state.get("error_category"):
        return "error_handler"
    return "profile_response_agent" if state.get("relevant") else "end"


def _route_after_response(state: ProfileState) -> str:
    return "error_handler" if state.get("error_category") else "contact_capture_agent"


def _route_after_contact(state: ProfileState) -> str:
    return "error_handler" if state.get("error_category") else "end"


def _build_graph():
    from langgraph.graph import END, START, StateGraph

    workflow = StateGraph(ProfileState)
    workflow.add_node(
        "profile_relevance_agent", _capture_node_errors(profile_relevance_agent)
    )
    workflow.add_node(
        "profile_response_agent", _capture_node_errors(profile_response_agent)
    )
    workflow.add_node(
        "contact_capture_agent", _capture_node_errors(contact_capture_agent)
    )
    workflow.add_node("error_handler", error_handler)
    workflow.add_edge(START, "profile_relevance_agent")
    workflow.add_conditional_edges(
        "profile_relevance_agent",
        _route_after_relevance,
        {
            "profile_response_agent": "profile_response_agent",
            "error_handler": "error_handler",
            "end": END,
        },
    )
    workflow.add_conditional_edges(
        "profile_response_agent",
        _route_after_response,
        {"contact_capture_agent": "contact_capture_agent", "error_handler": "error_handler"},
    )
    workflow.add_conditional_edges(
        "contact_capture_agent",
        _route_after_contact,
        {"error_handler": "error_handler", "end": END},
    )
    workflow.add_edge("error_handler", END)
    return workflow.compile()


profile_graph = _build_graph()


def run_profile_graph(question: str, history: list[dict[str, str]]) -> str:
    """Run the graph and convert any graph-level failure to a friendly result."""
    try:
        result = profile_graph.invoke({"question": question, "history": history[-12:]})
        return result.get(
            "answer",
            _friendly_error("UnexpectedError"),
        )
    except Exception as exc:  # noqa: BLE001 - catch graph execution failures at the UI boundary
        category, details = _safe_error(exc)
        try:
            append_error_log.invoke(
                {"error_category": category, "safe_diagnostic_details": details}
            )
        except Exception:  # noqa: BLE001 - the UI still needs a safe fallback
            return _friendly_error(category)
        return _friendly_error(category)