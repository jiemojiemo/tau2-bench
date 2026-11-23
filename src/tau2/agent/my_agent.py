from tau2.agent.llm_agent import LLMAgent, LLMAgentState
from tau2.environment.tool import Tool


class MyAgent(LLMAgent[LLMAgentState]):
    """Custom text agent that inherits the standard LLM agent behavior."""


def create_my_agent(tools: list[Tool], domain_policy: str, **kwargs) -> MyAgent:
    """Build MyAgent from the runner's agent settings."""
    return MyAgent(
        tools=tools,
        domain_policy=domain_policy,
        llm=kwargs.get("llm"),
        llm_args=kwargs.get("llm_args"),
        additional_stop_tool_names=kwargs.get(
            "additional_stop_tool_names", frozenset()
        ),
    )
