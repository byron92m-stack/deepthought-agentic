DeepThought — Agentic Orchestrator (v1.1)

DeepThought is a local-first agentic orchestration system designed to act as a
cognitive director for deterministic, auditable workflows.

It does not execute tasks autonomously.
Instead, it routes, supervises, and coordinates specialized nodes under a strict
operational contract.

This repository contains a reproducible v1.1-stable baseline validated end-to-end
with a local LLM backend.

------------------------------------------------------------

What this is (and is not)

This is:
- A LangGraph-based cognitive orchestrator
- A local-first system (no cloud dependency required)
- A deterministic and auditable controller for agentic workflows
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

- LLM layer
  Performs reasoning and supervision only.

- Tools layer
  Executes side-effectful actions under explicit contracts.

- Memory layer
  Explicit, versioned, and sanitized state.

Formal documentation:
- SYSTEM_DESIGN.md
- ARCHITECTURE.md
- NODE_CONTRACTS.md
- ROUTER_RULES.md
- MEMORY_MODEL.md
- PROMPT_DESIGN.md

------------------------------------------------------------

Baseline and Stability

This repository represents the v1.1-stable baseline.

Frozen elements:
- Graph structure and node roles
- Tool invocation via explicit tool_call
- Memory loading discipline
- Router decision flow

Out of scope for this baseline:
- Experimental integrations
- Cloud services
- Non-local inference backends

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

- Graph functional
- Router operational
- Tools node operational
- Memory baseline stable
- Local inference verified
- Repository is the single source of truth
