from project_finalizer.agents.runtime import AgentRuntimeCapabilities, ExternalAgentRuntime


def test_runtime_without_fresh_context_cannot_claim_independent_review() -> None:
    runtime = ExternalAgentRuntime(
        AgentRuntimeCapabilities(
            read_files=True,
            write_files=True,
            run_commands=True,
            fresh_context=False,
            parallel_agents=False,
        )
    )
    assert runtime.assurance_metadata()["independent_review"] is False
    assert runtime.network_calls_performed is False
