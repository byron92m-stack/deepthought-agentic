DeepThought — Router Rules (v2.0)

------------------------------------------------------------
1. Purpose of the Router

The router is the central decision-making component of the DeepThought v2.0 cognitive graph.

Its role is to analyze user input, evaluate context, and select the correct execution
path under deterministic rules.

In v2.0, routing is split into two explicit stages:
- router (path selection)
- agent_router (agent selection)

This separation ensures clarity, auditability, and strict cognitive discipline.

------------------------------------------------------------
2. Router Responsibilities

The router is responsible for:
- Classifying high-level user intent.
- Selecting exactly one valid execution path.
- Enforcing deterministic transitions.
- Preventing ambiguous or overlapping execution.
- Never executing reasoning, agents, or tools directly.
- Never modifying memory.

The router does NOT:
- Select agents directly.
- Execute tools.
- Perform reasoning.
- Mutate state beyond route selection.

------------------------------------------------------------
3. Router Inputs

The router evaluates the following inputs:

3.1 User Input
- keywords
- linguistic patterns
- explicit requests (e.g., “resume”, “qué recuerdas”)
- intent markers

3.2 Memory Context
- recent conversation history
- memory metadata (sizes, version)
- user/system profile (read-only)

3.3 Graph State
- previous node
- current execution phase

3.4 System Rules
- explicit routing rules defined in graph.py
- no probabilistic or heuristic routing

------------------------------------------------------------
4. Routing Logic (v2.0)

The router selects exactly one of the following paths:

- summarizer
- memory_query
- agent_router

No other routes are valid in v2.0.

------------------------------------------------------------
5. Routing Rules

5.1 Rule: summarizer

Triggered when the user explicitly requests condensation or summarization.

Examples:
- “resume…”
- “haz un resumen…”
- “summary…”
- “resumir conversación…”

Output:
- Next node: summarizer

------------------------------------------------------------

5.2 Rule: memory_query

Triggered when the user explicitly asks about stored memory or prior context.

Examples:
- “qué recuerdas”
- “que recuerdas”
- “memoria”
- “memory”
- “últimos mensajes”

Output:
- Next node: memory_query

------------------------------------------------------------

5.3 Rule: agent_pipeline (default)

Triggered for all other valid inputs.

This includes:
- analysis requests
- research requests
- commands
- financial questions
- marketing requests
- general problem solving
- greetings
- open-ended prompts

Output:
- Next node: agent_router

This rule is the default fallback and guarantees that all meaningful work
is handled by specialized agents.

------------------------------------------------------------
6. Deterministic Priority Order

When multiple rules match, the router applies the following priority:

1. memory_query
2. summarizer
3. agent_router (default)

This order is fixed and must not be changed without documentation.

------------------------------------------------------------
7. Agent Router Responsibilities (Context)

The agent_router is a separate node and is NOT part of the router.

Its responsibilities include:
- Selecting exactly one agent.
- Applying deterministic intent-to-agent rules.
- Writing state["agent_name"].
- Logging the selection.

The router must never bypass the agent_router.

------------------------------------------------------------
8. Invalid Transitions

The router explicitly prevents:
- Direct execution of agents.
- Direct execution of tools.
- Nodes calling each other directly.
- Recursive routing loops.
- Skipping memory management stages.

All valid execution paths must return control to the router or terminate
through memory_writer.

------------------------------------------------------------
9. Output Contract

The router must:
- Return exactly one valid next node.
- Produce no user-facing output.
- Leave memory untouched.
- Leave agent selection untouched.

Any deviation is considered a contract violation.

------------------------------------------------------------
10. Extending Router Rules

To add or modify router rules:

1) Update routing logic in graph.py.
2) Ensure the rule is deterministic.
3) Ensure it does not overlap existing rules ambiguously.
4) Document the change in this file.
5) Validate behavior through logs.

------------------------------------------------------------
11. Router Stability Guarantees

The router guarantees:
- Deterministic selection.
- Reproducible behavior.
- No hidden heuristics.
- No probabilistic routing.
- No agent overlap.
- No implicit execution.

------------------------------------------------------------
12. Verified Status (v2.0)

The router has been validated through manual certification:

- ResearchAgent routing
- ToolsAgent routing
- FinanceAgent routing
- MarketingAgent routing
- SupportAgent routing
- SalesAgent routing

Observed logs:
- Selected agent: research_agent
- Selected agent: tools_agent
- Selected agent: finance_agent
- Selected agent: marketing_agent
- Selected agent: support_agent
- Selected agent: sales_agent

------------------------------------------------------------
13. Stability Notice

This document reflects the system state as of v2.0-stable.

The following elements are considered frozen for the v2.0 baseline:
- Router path selection rules
- Deterministic priority order
- Separation between router and agent_router
- No implicit execution

Any future changes must be evaluated against this baseline.
