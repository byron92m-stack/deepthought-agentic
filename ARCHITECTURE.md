DeepThought — Cognitive Graph Architecture (v2.0)

------------------------------------------------------------
1. Overview

DeepThought v2.0 is a local-first cognitive orchestration system designed for
deterministic, auditable multi-agent workflows.

The system runs fully offline and is executed from the repository root.
This directory is the single source of truth for recovery, auditability,
and reproducible operation.

Version v2.0 introduces a multi-agent execution layer while preserving the
core architectural principles of v1.x:
explicit routing, explicit contracts, and no hidden execution.

------------------------------------------------------------
2. Project Structure

agenticai/
├── Modelfile
├── README.md
├── SYSTEM_DESIGN.md
├── ARCHITECTURE.md
├── NODE_CONTRACTS.md
├── ROUTER_RULES.md
├── MEMORY_MODEL.md
├── PROMPT_DESIGN.md
├── api.py
├── api_runs/
├── app/
│   ├── __init__.py
│   ├── graph.py
│   └── nodes/
├── agents/
│   ├── base_agent.py
│   ├── support_agent.py
│   ├── sales_agent.py
│   ├── research_agent.py
│   ├── tools_agent.py
│   ├── finance_agent.py
│   ├── marketing_agent.py
│   ├── prompts/
│   └── contracts/
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
  Node implementations (router, agent_router, agent_executor, memory_manager, etc.).

- agents/  
  Specialized agent implementations with explicit contracts.

- memory_v2_clean.json  
  Baseline sanitized memory snapshot used for recovery.

- api.py  
  Optional REST API interface.

- runs/  
  Logs for interactive executions.

- api_runs/  
  Logs for API executions.

- Modelfile  
  Local LLM configuration for offline inference.

------------------------------------------------------------
3. Execution Flow

3.1 Startup sequence

1) Load persistent memory via load_memory node.
2) Initialize graph state.
3) Initialize user/system profile (profile_initializer).
4) Initialize cognitive graph.
5) Enter interactive loop or API mode.

3.2 Interaction cycle (v2.0)

1) User provides input.
2) Router analyzes intent.
3) Router selects exactly one path:
   - summarizer
   - memory_query
   - agent pipeline
4) If agent pipeline:
   - agent_router selects exactly one agent
   - agent_executor executes the agent
5) Output is appended to state.
6) memory_manager applies deterministic memory rules.
7) memory_writer persists memory if configured.
8) Control returns to router.

------------------------------------------------------------
4. Cognitive Graph

The graph is defined in app/graph.py.

4.1 Nodes (v2.0)

- load_memory  
  Loads persistent memory into graph state.

- profile_initializer  
  Ensures a stable user/system profile exists.

- router  
  Selects the next execution path deterministically.

- summarizer  
  Produces executive summaries.

- memory_query  
  Answers explicit memory queries.

- agent_router  
  Selects exactly one agent based on deterministic intent rules.

- agent_executor  
  Executes the selected agent and returns structured output.

- memory_manager  
  Applies deterministic memory trimming and sanitization.

- memory_writer  
  Persists memory updates explicitly.

Nodes removed since v1.1:
- llm (generic)
- analysis
- command
- tools (direct execution)

All reasoning and coordination now occurs through agents.

------------------------------------------------------------
5. Multi-Agent Layer (Critical)

Agents are first-class execution units in v2.0.

Agents included in the baseline:
- support_agent
- sales_agent
- research_agent
- tools_agent
- finance_agent
- marketing_agent

Each agent:
- has a defined role and capabilities,
- receives (task, context),
- returns a structured dict,
- must respect explicit constraints.

Agents do not mutate memory directly.
Agents do not execute side effects implicitly.

------------------------------------------------------------
6. Tools Coordination

DeepThought v2.0 forbids implicit tool execution.

- Tool decisions are coordinated by tools_agent.
- Any side-effectful action must be explicit and auditable.
- No agent or node may execute tools directly without an explicit contract.

This preserves:
- determinism
- auditability
- separation of reasoning and action

------------------------------------------------------------
7. Memory System (v2)

7.1 Persistent memory

Baseline snapshot:
memory_v2_clean.json

Memory is:
- loaded explicitly at startup,
- injected into graph state,
- updated only via memory_manager and memory_writer.

7.2 Hybrid memory model

Memory segments:
- short_term
- long_term
- profile

Trimming and sanitization are deterministic and reproducible.

------------------------------------------------------------
8. Logging System

8.1 Interactive logs

Stored in:
runs/

8.2 API logs

Stored in:
api_runs/

Logs may include:
- input
- selected route
- selected agent
- node transitions
- outputs
- errors

------------------------------------------------------------
9. API Layer

api.py exposes the cognitive graph through a REST interface.

Example request:

curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'

The API executes the same graph as interactive mode.

------------------------------------------------------------
10. Local LLM Configuration

The Modelfile defines:
- model path
- inference parameters
- runtime configuration

This enables fully offline and reproducible inference.

------------------------------------------------------------
11. Architecture Diagram (Conceptual)

main.py
  |
  v
load_memory
  |
  v
profile_initializer
  |
  v
router
  |
  +--> summarizer
  |
  +--> memory_query
  |
  +--> agent_router
           |
           v
      agent_executor
           |
           v
      memory_manager
           |
           v
      memory_writer

------------------------------------------------------------
12. Recovery Assumptions

A valid recovery must satisfy:
- Python environment installs requirements successfully
- python main.py starts without exceptions
- agent routing behaves deterministically
- memory can be restored from memory_v2_clean.json

------------------------------------------------------------
13. Stability Notice

This document reflects the system state as of v2.0-stable.

Any future changes must be evaluated against this baseline.
