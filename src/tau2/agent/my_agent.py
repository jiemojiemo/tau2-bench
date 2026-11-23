from pathlib import Path

from tau2.agent.llm_agent import (
    AGENT_INSTRUCTION,
    SYSTEM_PROMPT,
    LLMAgent,
    LLMAgentState,
)
from tau2.environment.tool import Tool

_PROMPTS = Path(__file__).with_name("my_agent_prompts")


class MyAgent(LLMAgent[LLMAgentState]):
    """Custom text agent with airline-specific prompt text."""

    @property
    def system_prompt(self) -> str:
        """Fill the standard template with airline or default prompt text."""
        if any(tool.name == "book_reservation" for tool in self.tools):
            instructions = (
                (_PROMPTS / "airline_behavior.md").read_text(encoding="utf-8").strip()
            )
            policy = (_PROMPTS / "airline_rules.md").read_text(encoding="utf-8").strip()
        else:
            instructions = AGENT_INSTRUCTION
            policy = self.domain_policy

        return SYSTEM_PROMPT.format(
            agent_instruction=instructions, domain_policy=policy
        )


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
