DeepThought — Cognitive Graph Architecture (v1.1)

1. Overview

DeepThought is a local-first cognitive graph system designed for deterministic,
auditable orchestration of reasoning and controlled execution.

The system runs fully offline and is executed from:

/home/nw/agenticai

This directory is the single source of truth for recovery and operation.


------------------------------------------------------------
2. Project Structure

agenticai/
├── Modelfile
├── README.md
├── api.py
├── api_runs/
├── app/
│   ├── __init__.py
│   ├── graph.py
│   └── nodes/
├── main.py
├── memory_v2_clean.json
├── requirements.txt
├── runs/
└── venv/

Component roles:

- main.py
  Entry point and interactive orchestrator loop.

- app/graph.py
  Cognitive graph definition and node wiring.

- app/nodes/
  Node implementations (router, llm, analysis, tools, etc.).

- memory_v2_clean.json
  Baseline sanitized memory snapshot used for recovery.

- api.py
  Optional REST API interface.

- runs/
  Logs for interactive executions.

- api_runs/
  Logs for API executions.

- venv/
  Isolated Python environment.

- Modelfile
  Local LLM configuration for offline inference.


------------------------------------------------------------
3. Execution Flow

3.1 Startup sequence

1) Load persistent memory via load_memory node.
2) Initialize graph state.
3) Initialize cognitive graph.
4) Enter interactive loop or API mode.

3.2 Interaction cycle

1) User provides input.
2) Router analyzes intent.
3) Router selects exactly one next node.
4) Selected node executes.
5) Output is appended to state["messages"].
6) Control returns to router.


------------------------------------------------------------
4. Cognitive Graph

The graph is defined in app/graph.py.

4.1 Nodes

- load_memory
  Loads memory into graph state.

- router
  Selects the appropriate next node based on intent.

- llm
  General-purpose technical reasoning.

- analysis
  Structured deterministic reasoning.

- summarizer
  Executive summaries.

- command
  Technical command explanations.

- tools
  Controlled execution of side-effectful actions.


4.2 Router behavior

The router evaluates:
- user intent
- linguistic patterns
- memory context
- system state

It must:
- select exactly one valid node
- never execute tools directly
- never modify memory


------------------------------------------------------------
5. Tool Execution Layer (Critical)

All side-effectful actions are executed exclusively through the tools node.

Tool execution is requested via an explicit tool_call object in the graph state:

state["tool_call"] = {
    "name": "<tool_name>",
    "args": {...}
}

The tools node:
- executes the tool via the tool registry
- writes formatted output to state["output"]
- appends output to state["messages"]

Direct tool execution from LLM or router nodes is forbidden.

This guarantees:
- deterministic execution
- auditable state transitions
- separation of reasoning and action


------------------------------------------------------------
6. Memory System

6.1 Persistent memory

Baseline memory snapshot:

memory_v2_clean.json

Memory is:
- loaded explicitly at startup
- injected into graph state
- updated in memory state during execution

Persistence behavior depends on runtime configuration.

6.2 Profile

A persistent user profile may be created at runtime and reused across sessions.


------------------------------------------------------------
7. Logging System

7.1 Interactive logs

Stored in:

runs/

7.2 API logs

Stored in:

api_runs/

Logs may include:
- input
- selected route
- node transitions
- outputs
- errors


------------------------------------------------------------
8. API Layer

api.py exposes the cognitive graph through a REST interface.

Example request:

curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'

The API executes the same graph as the interactive mode.


------------------------------------------------------------
9. Local LLM Configuration

The Modelfile defines:
- model path
- inference parameters
- runtime configuration

This enables fully offline operation.


------------------------------------------------------------
10. Environment

DeepThought runs inside a Python virtual environment:

venv/

Dependencies are defined in:

requirements.txt


------------------------------------------------------------
11. Architecture Diagram (Conceptual)

main.py
  |
  v
load_memory
  |
  v
router
  |
  +--> llm
  |
  +--> analysis
  |
  +--> summarizer
  |
  +--> command
  |
  +--> tools


------------------------------------------------------------
12. Recovery Assumptions

A valid recovery must satisfy:
- Python environment installs requirements successfully
- python main.py starts without exceptions
- tools_node executes tools via tool_call contract
- memory can be restored from memory_v2_clean.json


------------------------------------------------------------
13. Stability Notice

This document reflects the system state as of v1.1-stable.

Any future changes must be evaluated against this baseline.
