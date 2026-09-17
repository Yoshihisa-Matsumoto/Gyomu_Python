from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionOption:
    """Action options for the llm process."""

    no_llm_request: bool = False
