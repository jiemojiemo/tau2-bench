"""Run one user turn through MyAgent and the real airline tools."""

from functools import cache

from tau2.data_model.message import AssistantMessage, ToolMessage, UserMessage
from tau2.data_model.tasks import InitialState, Task, UserScenario
from tau2.domains.airline.data_model import FlightDB
from tau2.domains.airline.environment import get_environment
from tau2.environment.environment import Environment
from tau2.multilingual.runtime import language_environment_kwargs, load_language
from tau2.orchestrator.orchestrator import Orchestrator
from tau2.runner.build import build_agent
from tau2.user.user_simulator import DummyUser
from tau2.user.user_simulator_base import STOP

MODEL = "openai/gpt-6-luna"
REASONING_EFFORT = "high"
MODEL_ARGS = {
    "reasoning_effort": REASONING_EFFORT,
    "allowed_openai_params": ["reasoning_effort"],
    "timeout": 60,
    "num_retries": 1,
}


@cache
def _regional_settings() -> dict:
    kwargs = language_environment_kwargs(load_language("zh", "airline", mode="text"))
    kwargs.pop("db")
    return kwargs


def booking_environment(initial_db: dict) -> Environment:
    """Create an isolated test database with the published Chinese airline policy."""
    return get_environment(
        db=FlightDB.model_validate(initial_db), **_regional_settings()
    )


class _SingleTurnUser(DummyUser):
    def generate_next_message(self, message, state):
        return UserMessage(role="user", content=STOP, cost=0), state


def target(inputs: dict) -> dict:
    """Resume from fixed history and run one new user turn."""
    environment = booking_environment(inputs["initial_db"])
    agent = build_agent(
        "my_agent",
        environment,
        llm=MODEL,
        llm_args=MODEL_ARGS,
        language="zh",
        language_guidance="请用简体中文回复用户。",
    )
    history = inputs.get("history", [])
    task = Task(
        id="level1-booking",
        user_scenario=UserScenario(instructions=""),
        initial_state=InitialState(
            message_history=[
                *history,
                UserMessage(role="user", content=inputs["user"], cost=0),
            ]
        ),
    )
    orchestrator = Orchestrator(
        domain="airline",
        agent=agent,
        user=_SingleTurnUser(),
        environment=environment,
        task=task,
        max_steps=16,
    )
    orchestrator.run()
    turns = orchestrator.trajectory[len(history) + 1 :]
    responses = [message for message in turns if isinstance(message, AssistantMessage)]
    successful = {
        message.id: message.content
        for message in turns
        if isinstance(message, ToolMessage) and not message.error
    }
    return {
        "answer": responses[-1].content
        if responses and not responses[-1].tool_calls
        else "",
        "db_hash": environment.get_db_hash(),
        "tool_calls": [
            {
                "name": call.name,
                "arguments": call.arguments,
                "ok": call.id in successful,
                "result": successful.get(call.id),
                "step": step,
            }
            for step, message in enumerate(responses, start=1)
            for call in message.tool_calls or ()
        ],
    }
