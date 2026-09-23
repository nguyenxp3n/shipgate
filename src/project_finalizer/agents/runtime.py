from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRuntimeCapabilities:
    read_files: bool
    write_files: bool
    run_commands: bool
    fresh_context: bool
    parallel_agents: bool


class ExternalAgentRuntime:
    """Provider-neutral boundary for exporting packets and importing observable outputs.

    V2 deliberately performs no network/provider API call. Integrations outside the deterministic
    core may hand a packet to a provider and return files for validation.
    """

    def __init__(self, capabilities: AgentRuntimeCapabilities) -> None:
        self.capabilities = capabilities
        self.network_calls_performed = False

    def assurance_metadata(self) -> dict[str, bool]:
        return {
            "independent_review": bool(self.capabilities.fresh_context),
            "parallel_agents": bool(self.capabilities.parallel_agents),
            "provider_execution_integration": False,
        }
