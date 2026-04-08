DeepThought — System Design Document (v2.0)

Baseline Header — v2.0 (Saneado)

This document describes the operational system design of DeepThought as of v2.0-stable.
Its primary goal is recovery and auditability: a new machine must be able to rebuild
and run the system using only this repository.

Frozen baseline elements (v2.0):
- Multi-agent routing flow (router → agent_router → agent_executor)
- Agent contract interface (task + context → structured dict output)
- Memory v2 discipline (explicit load, deterministic trimming policy, explicit persistence)
- Layer 2 (Operational Contract) and Layer 3 (User Model) as first-class context
- No implicit tool use (tools are coordinated under explicit contracts; no hidden execution)

Out of scope for baseline:
- Experimental integrations
- External cloud services
- Non-local inference backends
- Autonomous execution without explicit tool contracts
- Unbounded web browsing or non-auditable data acquisition

------------------------------------------------------------

1. Design Philosophy

DeepThought is designed as a deterministic cognitive graph rather than a monolithic
LLM wrapper. The system prioritizes:

- Modularity — each cognitive function is isolated in a node or agent.
- Determinism — routing selects exactly one next step under explicit rules.
- Transparency — every step is auditable through state and logs.
- Extensibility — new agents/nodes can be added without breaking the system.
- Persistence discipline — memory is explicit, versioned, and sanitized.
- Offline operation — the system runs fully local using a Modelfile-defined LLM.

v2.0 extends v1.1 by introducing a multi-agent layer while preserving the same core
principles: explicit transitions, explicit contracts, and no hidden execution.

------------------------------------------------------------

2. Core Components

2.1 Orchestrator (main.py)

The orchestrator is responsible for:
- loading persistent memory,
- initializing the graph state,
- instantiating the cognitive graph,
- running the interactive loop or API mode,
- delegating execution to the router.

The orchestrator supervises execution but does not perform reasoning or tool execution.

2.2 Agents (agents/*)

Agents are specialized handlers selected by the agent router. Each agent:
- has a role and capabilities,
- receives (task, context),
- returns a structured dict response,
- must respect constraints (e.g., no inventing unverifiable data).

Agents in v2.0 baseline:
- support_agent
- sales_agent
- research_agent
- tools_agent
- finance_agent
- marketing_agent

------------------------------------------------------------

3. Cognitive Graph Architecture

The cognitive graph is defined in app/graph.py.
It is a directed graph where each node represents a single cognitive function.

3.1 Node Types (v2.0)

- load_memory
  Injects persistent memory into graph state.

- profile_initializer
  Ensures a stable user/system profile exists and is not mutated implicitly.

- router
  Determines which path executes next (summarizer / memory_query / agent pipeline).

- summarizer
  Produces executive summaries under explicit constraints.

- memory_query
  Answers explicit memory questions under explicit constraints.

- agent_router
  Selects exactly one agent based on deterministic intent rules.

- agent_executor
  Executes the selected agent and returns structured output.

- memory_manager
  Applies deterministic memory management (sanitization, trimming policy, segmentation).

- memory_writer
  Persists memory updates according to runtime configuration.

Each node has:
- a defined purpose,
- an input contract,
- an output contract,
- a transition rule.

------------------------------------------------------------

4. Router Design

The router is the central decision-making component.

It evaluates:
- user intent,
- linguistic patterns,
- memory context,
- system state.

Router responsibilities:
- classify intent,
- select exactly one valid next node,
- enforce cognitive discipline,
- prevent invalid transitions,
- never execute tools directly,
- never modify memory directly.

4.1 Multi-agent routing (Critical)

In v2.0, general requests flow through:

router → agent_router → agent_executor

The agent_router:
- maps intent to exactly one agent,
- writes state["agent_name"] deterministically,
- logs the selection.

The agent_executor:
- loads the agent contract,
- passes (task, context),
- returns a structured dict response,
- does not execute side effects unless explicitly coordinated under contracts.

------------------------------------------------------------

5. Tools Coordination (Critical)

DeepThought does not allow implicit tool use.

In v2.0 baseline:
- tool decisions are coordinated by tools_agent (selection + argument validation),
- execution of side-effectful actions must remain explicit and auditable,
- direct tool execution from router or generic reasoning is forbidden.

If the repository includes a tools node/registry, it must be invoked only via explicit
state transitions and explicit tool_call objects, never implicitly.

This ensures deterministic and auditable execution.

------------------------------------------------------------

6. Memory System (v2)

6.1 Persistent Memory

Baseline memory snapshot:
memory_v2_clean.json

Memory is:
- loaded explicitly at startup,
- injected into graph state,
- updated only through memory_manager + memory_writer.

6.2 Hybrid memory model

Memory is segmented into:
- short_term: recent relevant messages
- long_term: sanitized summaries (deterministic trimming policy)
- profile: stable user/system profile

6.3 Constraints

- Memory must not be mutated implicitly by arbitrary nodes.
- Memory updates must be explicit, logged, and reproducible.
- Trimming/sanitization must be deterministic (no LLM-driven trimming).

------------------------------------------------------------

7. Layer 2 and Layer 3 Context

7.1 Layer 2 — Operational Contract

Layer 2 defines the operational constraints of the graph:
- determinism
- explicit transitions
- separation of reasoning and action
- auditability requirements
- structured response discipline

7.2 Layer 3 — User Model

Layer 3 defines user-specific operating parameters:
- communication style
- precision requirements
- reproducibility expectations
- constraints on assumptions

Both layers are treated as first-class context for routing and execution.

------------------------------------------------------------

8. Logging System

8.1 Interactive logs

Stored in:
runs/

8.2 API logs

Stored in:
api_runs/

Logs may include:
- input,
- selected route,
- selected agent,
- node transitions,
- outputs,
- errors.

Logs support debugging, auditing, and reproducibility.

------------------------------------------------------------

9. API Layer

api.py exposes the cognitive graph through a REST interface.

Example request:

curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'

The API executes the same graph as interactive mode.

------------------------------------------------------------

10. Local LLM Runtime

The Modelfile defines:
- model path,
- inference parameters,
- runtime configuration.

This enables fully offline and reproducible inference.

------------------------------------------------------------

11. Internal Data Flow

11.1 High-level flow (v2.0)

User Input
    ↓
main.py (orchestrator)
    ↓
load_memory
    ↓
profile_initializer
    ↓
router
    ↓
(agent path)
    ↓
agent_router
    ↓
agent_executor
    ↓
memory_manager
    ↓
memory_writer
    ↓
output

11.2 State propagation

Each node receives:
- current graph state,
- user input,
- memory context,
- Layer 2 + Layer 3 context (where applicable).

Each node returns:
- updated state,
- output,
- next node.

------------------------------------------------------------

12. Design Constraints

- The graph must remain deterministic.
- Memory must not be mutated implicitly.
- Router rules must be explicit and auditable.
- Nodes must not call each other directly.
- Tool execution must be explicit and auditable (no implicit tool use).
- Agent selection must be deterministic and logged.
- Agent outputs must be structured and contract-aligned.

------------------------------------------------------------

13. Extensibility Guidelines

13.1 Adding a new agent

1) Create the agent implementation in agents/.
2) Define role, capabilities, inputs/outputs, constraints.
3) Add/adjust deterministic routing rules in agent_router.
4) Add the agent contract JSON (if used).
5) Document the agent in NODE_CONTRACTS.md / AGENT_CONTRACTS.md (as applicable).

13.2 Adding a new node

1) Define the node function.
2) Specify purpose, input, output, and transition rule.
3) Register the node in the graph.
4) Update router rules if required.
5) Document the contract in NODE_CONTRACTS.md.

13.3 Modifying the router

Router changes must:
- be explicit,
- be documented,
- preserve existing valid transitions,
- avoid overlapping intent rules that reduce determinism.

------------------------------------------------------------

14. Risks and Limitations

- Router misclassification can lead to incorrect agent selection.
- Overlapping intent rules can reduce determinism.
- Memory corruption can affect routing and responses.
- Poorly defined contracts can destabilize the system.
- Side-effectful tools must remain explicitly controlled to preserve auditability.

------------------------------------------------------------

15. Evolution Roadmap (High level)

v2.1
- Agents with richer internal prompts and stricter output schemas
- Improved validation of agent outputs

v2.2
- Explicit tool registry expansion with stronger argument validation
- More auditable tool execution traces

v2.3
- Scheduler and recurring workflows (still explicit and auditable)

------------------------------------------------------------

16. Status (Verified)

- Graph functional.
- Router operational.
- Multi-agent routing operational.
- Agent executor operational.
- Memory v2 baseline stable.
- API available.
- Logs clean.
- Repository is the single source of truth.
