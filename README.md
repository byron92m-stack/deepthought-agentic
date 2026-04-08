DeepThought — Multi‑Agent Cognitive Orchestrator (v2.0)

DeepThought is a local-first cognitive orchestration system designed to act as a
deterministic, auditable director for multi-agent workflows.

It does not execute tasks autonomously.
Instead, it routes, supervises, and coordinates specialized agents and nodes under a strict
operational contract.

This repository contains the reproducible v2.0 baseline validated end-to-end
with a local LLM backend.

------------------------------------------------------------

What this is (and is not)

This is:
- A LangGraph-based cognitive orchestrator
- A local-first system (no cloud dependency required)
- A deterministic and auditable controller for agentic workflows
- A multi-agent routing + execution layer (router + agent_router + agent_executor)
- A foundation for disciplined multi-node reasoning and tool execution

This is not:
- A chatbot
- An autonomous executor
- A SaaS backend
- A prompt playground

------------------------------------------------------------

Architecture (high level)

Core layers:
- Router layer
  Selects exactly one next node under deterministic rules.

- Agent layer
  Routes to exactly one specialized agent and executes it under an explicit contract.

- LLM layer
  Performs reasoning and supervision only (no hidden execution).

- Tools layer
  Coordinates side-effectful actions under explicit contracts (no implicit tool use).

- Memory layer
  Explicit, versioned, sanitized state with hybrid memory v2.

Pipeline (v2.0):

input
  → load_memory
  → profile_initializer
  → router
      → agent_router
      → agent_executor
  → memory_manager
  → memory_writer
  → output

Graph (ASCII):

                          ┌──────────────────────┐
                          │      input text       │
                          └──────────┬───────────┘
                                     │
                           ┌─────────▼─────────┐
                           │    load_memory     │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │ profile_initializer│
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │      router        │
                           └─────────┬─────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
          ┌─────────▼─────────┐             ┌────────▼────────┐
          │   summarizer       │             │  memory_query    │
          └─────────┬─────────┘             └────────┬────────┘
                    │                                 │
                    └─────────────────────────────────┘
                                     │
                           ┌─────────▼─────────┐
                           │   agent_router     │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │  agent_executor    │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │  memory_manager    │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │  memory_writer     │
                           └─────────┬─────────┘
                                     │
                           ┌─────────▼─────────┐
                           │      output        │
                           └────────────────────┘

Agents (v2.0):
- support_agent   (Soporte técnico y operativo)
- sales_agent     (Ventas y prospección)
- research_agent  (Investigación y análisis)
- tools_agent     (Coordinación de herramientas)
- finance_agent   (Finanzas y análisis económico)
- marketing_agent (Marketing y contenido)

Formal documentation:
- SYSTEM_DESIGN.md
- ARCHITECTURE.md
- NODE_CONTRACTS.md
- ROUTER_RULES.md
- MEMORY_MODEL.md
- PROMPT_DESIGN.md

------------------------------------------------------------

Baseline and Stability

This repository represents the v2.0-stable baseline.

Frozen elements (v2.0 baseline):
- Multi-agent routing flow (router → agent_router → agent_executor)
- Agent contract interface (task + context → structured dict output)
- Memory v2 discipline (explicit load, deterministic trimming policy, explicit persistence)
- No implicit tool use (tools are coordinated under explicit contracts)

Out of scope for this baseline:
- Experimental integrations
- Cloud services
- Non-local inference backends
- Autonomous execution without explicit tool contracts

------------------------------------------------------------

Requirements

System:
- Linux / macOS / WSL2
- Python 3.10+
- Git

LLM backend:
- Ollama (local inference)

------------------------------------------------------------

Install Ollama

If Ollama is not installed (Linux / WSL):

curl -fsSL https://ollama.com/install.sh | sh

Ensure the Ollama service is running before starting DeepThought.

------------------------------------------------------------

Setup

Clone the repository:

git clone <repository-url>
cd agenticai

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

------------------------------------------------------------

Local LLM Setup

Build the local model defined in Modelfile:

ollama create deepthought -f Modelfile

------------------------------------------------------------

Run the System

Start the interactive orchestrator:

python main.py

The system will:
- load baseline memory
- initialize the cognitive graph
- enter the interactive loop

------------------------------------------------------------

Testing

Core tests (must pass for a valid recovery):
- test_tools_node.py

Experimental tests (not part of baseline):
- test_autogen.py

Manual certification (v2.0 agents):
- support_agent:  "hola deepthought, tengo un problema con mi pipeline de ingest"
- sales_agent:    "redacta un mensaje de prospección para un cliente B2B"
- research_agent: "analiza el mercado de tarjetas cripto en LATAM"
- tools_agent:    "dame un comando curl para hacer POST con JSON a esta URL: https://api.test.com/x"
- finance_agent:  "calcula el pnl diario de este portafolio"
- marketing_agent:"escribe un tweet promocionando un nuevo producto fintech"

Expected behavior:
- Selected agent: <agent_name>
- agent_executor runs the agent
- structured JSON output returned
- memory_manager + memory_writer persist state

------------------------------------------------------------

Memory and Recovery

Baseline memory snapshot:
- memory_v2_clean.json

Memory is loaded explicitly at startup.
Persistence behavior depends on runtime configuration.

For recovery, the baseline memory snapshot is sufficient.

------------------------------------------------------------

API (Optional)

The cognitive graph can be exposed via a REST API.

Example request:

curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'

The API executes the same graph as interactive mode.

------------------------------------------------------------

Project Philosophy

- Determinism first
- Explicit state and transitions
- No hidden execution
- No implicit tool use
- Clear separation of reasoning and action

------------------------------------------------------------

Status

- v2.0 certified
- Multi-agent router operational
- Agent executor operational
- 6 agents operational (support/sales/research/tools/finance/marketing)
- Memory v2 baseline stable
- Local inference verified
- Repository is the single source of truth
