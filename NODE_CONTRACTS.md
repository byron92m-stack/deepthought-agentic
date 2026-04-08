DeepThought — Node Contracts (v2.0)

1. Purpose of This Document

This document defines the formal contracts for every node in the DeepThought v2.0 cognitive graph.

A node contract specifies:
- purpose
- inputs
- outputs
- state usage
- transition rules
- constraints
- failure modes

These contracts ensure deterministic behavior, auditability, and safe extensibility.
Any implementation that violates these contracts is considered invalid.

------------------------------------------------------------

2. Node: load_memory

Purpose:
Load persistent memory and inject it into the graph state.

Input:
- state (empty or minimal)
- user_input (ignored)

Output:
Updated state containing (at minimum):
- messages (list)
- memory (or equivalent memory container)
- memory_meta (versioning metadata, if present)

Next node: profile_initializer
No user-facing message.

Constraints:
- Must not generate LLM output
- Must not invent memory fields not supported by the memory schema
- Must not mutate memory content beyond loading/parsing

Failure Modes:
- Missing file / corrupted JSON → fallback to empty memory structure + log error
- Schema mismatch → sanitize to minimal valid structure + log warning

------------------------------------------------------------

3. Node: profile_initializer

Purpose:
Ensure a stable user/system profile exists in state and is safe to use for routing and execution.

Input:
- state (with memory loaded)
- user_input (ignored)

Output:
Updated state containing (at minimum):
- profile.user (must exist; if already exists, must not be modified)
- profile.system (optional, if used)
- any required defaults for v2.0 routing/execution

Next node: router
No user-facing message.

Constraints:
- Must be deterministic
- Must not overwrite an existing profile.user
- Must not call LLM or tools

Failure Modes:
- Missing profile container → create minimal profile structure
- Invalid profile fields → sanitize to minimal valid structure + log warning

------------------------------------------------------------

4. Node: router

Purpose:
Select the correct cognitive path based on user intent.

Input:
- state
- user_input

Output:
Next node: exactly one of
- summarizer
- memory_query
- agent_router

No user-facing message.

Constraints:
- Must return exactly one valid next node
- Must not call nodes directly
- Must not modify memory
- Must be deterministic given the same (state, user_input)

Failure Modes:
- Ambiguous intent → fallback to agent_router
- Invalid state → fallback to agent_router + log warning

------------------------------------------------------------

5. Node: summarizer

Purpose:
Produce an executive summary of prior conversation/output.

Input:
- state (messages + relevant context)
- user_input (may specify what to summarize)

Output:
- Summary appended to state["messages"]
- Optional: state["last_output"] updated with summary text

Next node: memory_manager

Constraints:
- No new information
- No interpretation beyond summarization
- Must not modify memory directly

Failure Modes:
- Not enough context → return a minimal summary stating insufficient context
- Output too long → truncated by orchestrator policy

------------------------------------------------------------

6. Node: memory_query

Purpose:
Answer explicit questions about stored memory/state (e.g., “qué recuerdas”, “últimos mensajes”, etc.).

Input:
- state (memory + messages)
- user_input (explicit memory question)

Output:
- Answer appended to state["messages"]
- Optional: state["last_output"] updated with answer text

Next node: memory_manager

Constraints:
- Must only use available memory/state (no invention)
- Must not modify memory directly
- Must respect memory visibility rules (if any)

Failure Modes:
- Memory not available → respond with “no memory loaded” (or equivalent) + log warning
- Query not supported → respond with “unsupported memory query” (or equivalent)

------------------------------------------------------------

7. Node: agent_router

Purpose:
Select exactly one specialized agent based on deterministic intent rules.

Input:
- state
- user_input

Output:
Updated state containing:
- agent_name (string; one of the registered agents)
- agent_task (string; normalized task derived from user_input)
- agent_context (object; includes memory_meta/profile as needed)

Next node: agent_executor
No user-facing message.

Constraints:
- Must select exactly one valid agent
- Must be deterministic given the same (state, user_input)
- Must not execute the agent
- Must not modify memory

Failure Modes:
- No match → fallback to a default agent (typically support_agent or research_agent) + log warning
- Multiple matches → apply priority rules deterministically + log decision

------------------------------------------------------------

8. Node: agent_executor

Purpose:
Execute the selected agent under its explicit contract and return structured output.

Input:
State containing (at minimum):
- agent_name
- agent_task
- agent_context

Output:
- Agent response appended to state["messages"] (or stored in state["last_output"])
- Optional: state["agent_result"] stored as structured dict for downstream processing

Next node: memory_manager

Constraints:
- Must not change agent selection
- Must not modify memory directly
- Must preserve structured output (dict/JSON-like) if the agent returns it
- Must enforce agent contract boundaries (inputs/outputs)

Failure Modes:
- Missing agent_name → return structured error + log error
- Unknown agent_name → return structured error + log error
- Agent exception → return structured error payload + log stack trace (if enabled)

------------------------------------------------------------

9. Node: memory_manager

Purpose:
Apply deterministic memory management after each user-visible output:
- sanitization
- segmentation (short_term / long_term / profile)
- trimming policy
- memory_meta updates

Input:
- state (including latest messages/output)
- user_input (optional; usually ignored)

Output:
Updated state containing:
- updated memory structure (in-memory only)
- updated memory_meta (version, sizes, timestamps if used)

Next node: memory_writer
No user-facing message.

Constraints:
- Must be deterministic (no LLM-driven trimming)
- Must not invent facts
- Must not remove required schema fields
- Must not reorder history in a way that breaks auditability

Failure Modes:
- Memory schema invalid → sanitize to minimal valid structure + log warning
- Trimming policy error → skip trimming + log error

------------------------------------------------------------

10. Node: memory_writer

Purpose:
Persist memory updates explicitly according to runtime configuration.

Input:
- state (with updated memory)
- user_input (ignored)

Output:
- Memory persisted to configured storage (e.g., JSON file)
- Optional: state["memory_write_status"] updated

Next node: output (end of cycle)
No user-facing message.

Constraints:
- Must not modify memory content (only write)
- Must be explicit and auditable (log write success/failure)
- Must not block the system indefinitely (timeouts/guards recommended)

Failure Modes:
- Write failure (permissions/disk) → log error; continue without crashing if policy allows
- Partial write → log error; attempt safe rollback if implemented

------------------------------------------------------------

11. Removed Nodes (v1.1 → v2.0)

The following v1.1 nodes are not part of the v2.0 baseline node set:
- llm
- analysis
- command
- tools (direct tool execution node)

Their responsibilities are replaced by:
- agent_router + agent_executor (specialized agents)
- tools_agent (coordination/validation of tool usage, if applicable)

------------------------------------------------------------

12. Adding New Nodes (Contract Requirements)

Any new node must define:
- purpose
- input contract
- output contract
- state usage
- transition rule
- constraints
- failure modes

The contract must be documented here before implementation.

------------------------------------------------------------

Stability Notice

This document reflects the system state as of v2.0-stable.

The following elements are considered frozen for the v2.0 baseline:
- Multi-agent routing flow (router → agent_router → agent_executor)
- Node contracts defined in this document
- Memory v2 handling via memory_manager + memory_writer
- Deterministic routing and explicit transitions

Any future changes must be evaluated against this baseline.
