"""Opt-in LangSmith tracing for simulation runs."""

import os
from contextlib import contextmanager, nullcontext
from contextvars import ContextVar
from functools import cache, wraps

_agent_turn = ContextVar("tau2_tracing_agent_turn", default=False)


def tracing_enabled() -> bool:
    """Return whether the run opted into LangSmith."""
    return os.getenv("LANGSMITH_TRACING", "").lower() == "true"


def traceable(**options):
    """Load the optional LangSmith decorator when tracing is first enabled."""

    def decorate(func):
        @cache
        def traced():
            try:
                from langsmith import traceable as sdk_traceable
            except ImportError as exc:
                raise RuntimeError(
                    "Install the LangSmith extra with uv sync --frozen --extra langsmith."
                ) from exc
            return sdk_traceable(**options)(func)

        @wraps(func)
        def invoke(*args, **kwargs):
            return (traced() if tracing_enabled() else func)(*args, **kwargs)

        return invoke

    return decorate


@contextmanager
def trace_agent_turn():
    """Allow model inputs and outputs to be traced during an agent turn."""
    token = _agent_turn.set(True)
    try:
        yield
    finally:
        _agent_turn.reset(token)


def trace_child(name, *, run_type, inputs, metadata=None):
    """Record model spans only while the customer-service agent is acting."""
    if not tracing_enabled() or (run_type == "llm" and not _agent_turn.get()):
        return nullcontext()
    from langsmith import get_current_run_tree, trace

    if get_current_run_tree() is None:
        return nullcontext()
    return trace(name, run_type=run_type, inputs=inputs, metadata=metadata)


def current_trace_ref() -> dict[str, str] | None:
    """Return the active run's location for linking from an experiment row."""
    if not tracing_enabled():
        return None
    from langsmith import get_current_run_tree

    run = get_current_run_tree()
    return {"id": str(run.id), "project": run.session_name} if run else None
