from pathlib import Path

from tau2.agent.llm_agent import (
    AGENT_INSTRUCTION,
    SYSTEM_PROMPT,
    LLMAgent,
    LLMAgentState,
)
from tau2.environment.tool import Tool

_PROMPTS = Path(__file__).with_name("my_agent_prompts")
_AIRLINE_RUNTIME_CONTEXT = """

<runtime_context>
Scenario time: 2024-05-15T15:00:00+08:00 (Asia/Shanghai).
Use this clock for relative dates and to decide whether a departure is in the past.
</runtime_context>"""


class MyAgent(LLMAgent[LLMAgentState]):
    """Custom text agent with airline-specific prompt text."""

    @property
    def system_prompt(self) -> str:
        """Fill the standard template with airline or default prompt text."""
        runtime_context = ""
        if any(tool.name == "book_reservation" for tool in self.tools):
            instructions = (
                (_PROMPTS / "airline_behavior.md").read_text(encoding="utf-8").strip()
            )
            policy = (_PROMPTS / "airline_rules.md").read_text(encoding="utf-8").strip()
            runtime_context = _AIRLINE_RUNTIME_CONTEXT
        else:
            instructions = AGENT_INSTRUCTION
            policy = self.domain_policy

        system_prompt = SYSTEM_PROMPT.format(
            agent_instruction=instructions, domain_policy=policy
        )
        return system_prompt + runtime_context


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
