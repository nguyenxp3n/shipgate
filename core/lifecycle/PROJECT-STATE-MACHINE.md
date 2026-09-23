# Project State Machine

The canonical lifecycle is `RAW_INPUT → INTAKE_COMPLETE → SOURCE_NORMALIZED → CORE_SPEC_FROZEN → MACHINE_CONTRACTS_READY → AGENT_SPEC_READY → WORK_PACKAGES_READY → SENIOR_AUDITED → CORRECTIVE_COMPLETE → BUILD_READY → FINAL_RELEASE`.

Transitions are validated against an explicit adjacency map. Agents cannot edit state directly to bypass gates.
