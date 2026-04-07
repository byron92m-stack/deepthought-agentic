DeepThought — System Design Document (v1.1)

Baseline Header — v1.1 (Saneado)

This document describes the operational system design of DeepThought as of v1.1-stable.
Its primary goal is recovery and auditability: a new machine must be able to rebuild
and run the system using only this repository.

Frozen baseline elements:
- Graph structure and node roles
- Node contracts (see NODE_CONTRACTS.md)
- Tool invocation via state["tool_call"]
- Memory loading discipline (explicit, versioned)
- Router decision flow (select exactly one next node)

Out of scope for baseline:
- Experimental integrations
- External cloud services
- Non-local inference backends

------------------------------------------------------------

1. Design Philosophy

DeepThought is designed as a deterministic cognitive graph rather than a monolithic
LLM wrapper. The system prioritizes:

- Modularity — each cognitive function is isolated in a node.
- Determinism — the router selects nodes based on explicit rules.
- Transparency — every step is auditable through state and logs.
- Extensibility — new nodes can be added without breaking the system.
- Persistence discipline — memory is explicit and versioned.
- Offline operation — the system runs fully local using a Modelfile-defined LLM.

This design ensures reproducibility, auditability, and controlled cognitive behavior.

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

------------------------------------------------------------

3. Cognitive Graph Architecture

The cognitive graph is defined in app/graph.py.
It is a directed graph where each node represents a single cognitive function.

3.1 Node Types

- load_memory
  Injects persistent memory into graph state.

- router
  Determines which node should execute next.

- llm
  General-purpose technical reasoning.

- analysis
  Structured deterministic reasoning.

- summarizer
  Executive summaries.

- command
  Technical command explanations.

- tools
  Controlled execution of side-effectful actions via tool_call.

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
- never modify memory.

------------------------------------------------------------

4.1 Tools Execution (Critical)

All side-effectful actions are executed exclusively through the tools node.

Tool execution is requested via an explicit tool_call object in the graph state:

state["tool_call"] = {
    "name": "<tool_name>",
    "args": {...}
}

The tools node:
- executes the tool via the tool registry,
- writes formatted output to state["output"],
- appends output to state["messages"],
- returns control to the router.

Direct tool execution from LLM or router nodes is forbidden.
This ensures deterministic and auditable execution.

------------------------------------------------------------

5. Memory System

5.1 Persistent Memory

Baseline memory snapshot:
memory_v2_clean.json

Memory is:
- loaded explicitly at startup,
- injected into graph state,
- updated in memory state during execution.

Persistence behavior depends on runtime configuration.

5.2 Profile

A persistent user profile may be created at runtime and reused across sessions.

------------------------------------------------------------

6. Logging System

6.1 Interactive logs

Stored in:
runs/

6.2 API logs

Stored in:
api_runs/

Logs may include:
- input,
- selected route,
- node transitions,
- outputs,
- errors.

Logs support debugging, auditing, and reproducibility.

------------------------------------------------------------

7. API Layer

api.py exposes the cognitive graph through a REST interface.

Example request:

curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'

The API executes the same graph as interactive mode.

------------------------------------------------------------

8. Local LLM Runtime

The Modelfile defines:
- model path,
- inference parameters,
- runtime configuration.

This enables fully offline and reproducible inference.

------------------------------------------------------------

9. Internal Data Flow

9.1 High-level flow

User Input
    ↓
main.py (orchestrator)
    ↓
load_memory
    ↓
router
    ↓
selected node (llm / analysis / summarizer / command / tools)
    ↓
output appended to state
    ↓
return to router

9.2 State propagation

Each node receives:
- current graph state,
- user input,
- memory context.

Each node returns:
- updated state,
- output,
- next node.

------------------------------------------------------------

10. Design Constraints

- The graph must remain deterministic.
- Memory must not be mutated implicitly.
- Router rules must be explicit and auditable.
- Nodes must not call each other directly.
- Tool execution must occur only through tools node.

------------------------------------------------------------

11. Extensibility Guidelines

11.1 Adding a new node

1) Define the node function.
2) Specify purpose, input, output, and transition rule.
3) Register the node in the graph.
4) Update router rules if required.
5) Document the contract in NODE_CONTRACTS.md.

11.2 Modifying the router

Router changes must:
- be explicit,
- be documented,
- preserve existing valid transitions.

------------------------------------------------------------

12. Risks and Limitations

- Router misclassification can lead to incorrect node selection.
- Memory corruption can affect reasoning.
- Poorly defined node contracts can destabilize the graph.
- Overlapping node responsibilities can cause ambiguity.

------------------------------------------------------------

13. Evolution Roadmap

v1.2
- validation layer for node outputs
- router rule hardening

v1.3
- structured memory segmentation
- improved audit tooling

------------------------------------------------------------

14. Status (Verified)

- Graph functional.
- Router operational.
- Tools node operational.
- Memory baseline stable.
- API available.
- Logs clean.
- Repository is the single source of truth.
