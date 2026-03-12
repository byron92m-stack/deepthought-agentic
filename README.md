# deepthought-agentic (v1.1)

Deterministic, modular agentic AI architecture for reproducible reasoning, explicit memory, and clean orchestration.
Runs locally with Ollama + a cognitive graph (graph.py) + optional FastAPI exposure.

---

## What this repo is

deepthought-agentic is a local “cognitive agent” system with three strict layers:

1) Identity (Model Constitution)
- Defined only in: Modelfile

2) Cognition (Reasoning + Control Flow + Memory I/O)
- Defined only in: app/graph.py

3) Exposure (How you run it)
- CLI: main.py
- API: api.py (FastAPI)

The goal is operational clarity:
- No duplicated prompts
- No hidden system_prompt files
- No legacy memory files in runtime
- One memory file, explicitly read/written

---

## Repository structure
```
.
├── Modelfile
├── README.md
├── api.py
├── main.py
├── requirements.txt
├── run_local.py
└── app
    ├── __init__.py
    ├── graph.py
    └── memory_v2_clean.json
```
Additional local components (not versioned / not required for recovery):
- api_runs/  → API execution logs (local)
- runs/      → graph execution logs (local)
- venv/      → local Python environment (local)

If you clone this repo on a new machine, you only need the versioned files above.

---

## 🧠 Cognitive architecture (v1.1)

Deepthought is built around a deterministic cognitive graph that separates identity, reasoning, memory, and execution.

High-level mental model:
```
┌──────────────────────────────┐
│        Model Identity        │
│          (Modelfile)         │
│  Executive persona & rules   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Cognitive Graph Core     │
│        (app/graph.py)        │
│  Routing, reasoning, memory  │
└──────────────┬───────────────┘
               │
     ┌─────────┴─────────┐
     ▼                   ▼
┌──────────────┐   ┌────────────────┐
│ Reasoning    │   │ Memory Manager │
│ Nodes        │   │ Persistent JSON│
│ (LLM calls)  │   │ (v2_clean)     │
└──────────────┘   └────────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Execution Interface      │
│   CLI (main.py) / API        │
│   (FastAPI / uvicorn)        │
└──────────────────────────────┘
```
Core components:

- Model Identity (Modelfile)
  - Defines executive identity, constraints, and high-level posture.
  - Immutable at runtime (the “constitution”).

- Cognitive Graph (app/graph.py)
  - Single source of truth for reasoning flow.
  - Responsible for:
    - input routing
    - node execution
    - memory reads/writes
    - deterministic control flow

- Memory (app/memory_v2_clean.json)
  - Persistent explicit memory store.
  - No hidden state.
  - All memory mutations are intentional and traceable.

- Execution layer
  - CLI: main.py
  - API: api.py (FastAPI)

Design principles enforced in v1.1:
- Single source of truth (identity/cognition/memory each live in exactly one place)
- Determinism first (same input + same memory => same behavior)
- No hidden prompts (no parallel system_prompt files)
- Auditability (reasoning steps + memory mutations are inspectable)
- Scalable by extension (add nodes/agents without contaminating the core)

---

## 📦 Versioning & recovery (GitHub)

This repository preserves multiple reference points for safe recovery and controlled evolution.

Branches:
- main
  - Historical baseline (v1.0). Minimal architecture preserved for reference.

- v1.1-dev
  - Active development branch built on top of the v1.1 stable baseline.

Tags:
- v1.1-stable
  - Frozen, audited baseline for recovery.
  - Recommended restore point for “clean v1.1”.

Recovery from any machine (stable baseline):
1) Clone
   git clone https://github.com/byron92m-stack/deepthought-agentic
2) Enter repo
   cd deepthought-agentic
3) Checkout stable baseline
   git checkout v1.1-stable

Continue development:
- git checkout v1.1-dev

Verify you have the tag locally:
- git fetch --tags
- git tag
- git show v1.1-stable --oneline

---

## Requirements (for a fresh machine)

You need:
- Python 3.10+ (recommended)
- pip
- Ollama installed and available in PATH
- A local LLM pulled/available via Ollama

Optional:
- uvicorn (installed via requirements.txt)
- curl (for API testing)

---

## Setup (fresh machine)

1) Create and activate a virtual environment (recommended)

Linux/macOS:
- python -m venv venv
- source venv/bin/activate

Windows PowerShell:
- python -m venv venv
- .\venv\Scripts\Activate.ps1

2) Install dependencies
- pip install -r requirements.txt

3) Start Ollama
- ollama serve

4) Build/create the model defined by Modelfile
- ollama create deepthought -f Modelfile

Notes:
- The model name used by this project is: deepthought
- If you change it, update your runtime calls accordingly.

---

## Running the project (CLI)

Run the cognitive graph:
- python main.py

This should start the interactive loop (or whatever main.py implements in your current v1.1).

---

## Running the project (API)

Start the API server:
- uvicorn api:app --reload --port 8000

Endpoint:
- POST /deepthought-graph

Example request:
curl -X POST http://localhost:8000/deepthought-graph \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello deepthought"}'

If your API expects a different JSON key than "input", update the curl payload to match api.py.

---

## Operational notes (reproducibility)

To keep behavior reproducible:
- Do not add extra prompt files (no system_prompt.txt in runtime).
- Keep identity only in Modelfile.
- Keep cognition only in app/graph.py.
- Keep memory only in app/memory_v2_clean.json.

If you want experiments:
- Do them on v1.1-dev (branch), not on the v1.1-stable tag.

---

## Troubleshooting

Ollama not responding:
- Ensure it is running: ollama serve
- Ensure the model exists: ollama list
- Recreate model if needed: ollama create deepthought -f Modelfile

API runs but endpoint fails:
- Confirm uvicorn is running on port 8000
- Confirm route exists in api.py: /deepthought-graph
- Confirm request JSON matches what api.py expects

Import errors:
- Reinstall deps: pip install -r requirements.txt
- Ensure you are in the venv
- Ensure you are running from repo root

---

## Roadmap

v1.1 — Full Cognitive Graph (current)
- Deterministic reasoning graph
- Persistent memory
- Clean separation of concerns

v2.0 — Multi-Agent Swarm
- Executive director agent
- Specialized executor agents
- Internal evaluation loops
- Dynamic orchestration

v3.0 — Integrations
- ETL pipelines
- Trading systems
- Monitoring agents
- Local GUI

---

## Project philosophy

- Determinism first: reproducible behavior across runs
- Strict modularity: identity, cognition, and exposure remain separate
- Scalable design: minimal core, expandable architecture
- Operational clarity: no contamination, no ambiguity, no hidden state

---

## About

AI Engineer | Agentic Systems Architect | LLM Orchestration | LangGraph & Ollama | Backend & Workflow Architecture | Open to Work

I design and build modular agentic AI systems with a strong focus on deterministic behavior, cognitive architecture, and workflow orchestration. My work blends LLM engineering, backend architecture, and systems design, creating agents that are reproducible, interpretable, and ready for real-world integration.

Contact:
Email: byron92m@gmail.com
GitHub: https://github.com/byron92m-stack
(Open to remote roles worldwide)
