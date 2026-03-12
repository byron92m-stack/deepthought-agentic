# deepthought-agentic (v1.1)

Deterministic, modular agentic AI architecture for reproducible reasoning, explicit memory, and clean orchestration.
Designed for local execution using Ollama, a deterministic cognitive graph (LangGraph), and optional FastAPI exposure.

This repository is engineered so the entire system can be recovered from scratch on a new machine (Linux, WSL2, or macOS) with no hidden state, no legacy files, and no undocumented dependencies.

---

## What this project is

deepthought-agentic is a local cognitive-agent system built around three strictly separated layers:

1) Identity
- Defined only in `Modelfile`.
- Executive constitution: persona, constraints, and high-level reasoning posture.

2) Cognition
- Defined only in `app/graph.py`.
- Deterministic cognitive graph responsible for routing, reasoning, and memory I/O.

3) Exposure
- CLI: `main.py`
- API: `api.py` (FastAPI)

There are no parallel prompts, no hidden system files, and no implicit memory.

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
Local-only (not versioned, not required for recovery):
- api_runs/  → API execution logs
- runs/      → graph execution logs
- venv/      → local Python virtual environment

Only the versioned files above are required to recover the project on a new machine.

---

## 🧠 Cognitive architecture (v1.1)

Deepthought is built around a deterministic cognitive graph that cleanly separates identity, reasoning, memory, and execution.

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
Design principles enforced in v1.1:
- Single source of truth per layer
- Determinism first (same input + same memory = same behavior)
- No hidden prompts or legacy files
- Full auditability (prompts + memory mutations visible)
- Scalable by extension, not mutation

---

## 📦 Versioning & recovery (GitHub)

Branches:
- `main` → historical baseline (v1.0)
- `v1.1-dev` → active development

Tags:
- `v1.1-stable` → frozen, audited recovery baseline

Recovery from any machine:
git clone https://github.com/byron92m-stack/deepthought-agentic
cd deepthought-agentic
git checkout v1.1-stable

---

## Platform support

Supported environments:
- Linux (recommended)
- Windows + WSL2 (fully supported)
- macOS

No OS-specific code paths are used in the cognitive layer.

---

## Requirements (fresh machine)

- Python 3.10+
- pip
- Git
- Ollama installed and available in PATH

All Python dependencies are defined in `requirements.txt`.

---

## Linux setup (native)

1) System dependencies:
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl git

2) Install Ollama:
curl -fsSL https://ollama.com/install.sh | sh

3) Clone and checkout:
git clone https://github.com/byron92m-stack/deepthought-agentic
cd deepthought-agentic
git checkout v1.1-stable

4) Python environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

5) Start Ollama and create the model:
ollama serve
ollama create deepthought -f Modelfile

---

## Windows + WSL2 setup (IMPORTANT)

This project runs inside WSL. WSL is not “just Linux”; it is Linux + Windows + a hybrid filesystem and networking layer.

### WSL requirements
- Windows 10/11
- WSL2 enabled
- Ubuntu 22.04+ recommended

### Critical WSL rules (reproducibility + performance)
- Recommended: keep the repo inside the Linux filesystem:
  /home/<user>/deepthought-agentic
- Avoid running from Windows-mounted drives (/mnt/c, /mnt/e) for heavy I/O.
- If you do run from /mnt/*, it will work, but file I/O can be slower and permissions can behave differently.

### Your current setup (documented)
Your current `graph.py` uses:
MEMORY_FILE = "/mnt/e/agentic/app/memory_v2_clean.json"

That means:
- The memory file is stored on a Windows-mounted drive.
- Recovery on a new PC must either:
  A) preserve the same path convention, or
  B) change MEMORY_FILE to a repo-relative path (recommended).

Recommended improvement (portable path):
Set MEMORY_FILE to:
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_v2_clean.json")

This makes recovery independent of drive letters and mount points.

### Setup steps (WSL)
1) Install WSL (PowerShell):
wsl --install

2) Open Ubuntu (WSL terminal)

3) Install system dependencies:
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl git

4) Install Ollama inside WSL:
curl -fsSL https://ollama.com/install.sh | sh

5) Clone and checkout:
git clone https://github.com/byron92m-stack/deepthought-agentic
cd deepthought-agentic
git checkout v1.1-stable

6) Python environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

7) Start Ollama and create the model:
ollama serve
ollama create deepthought -f Modelfile

### Networking note (WSL)
- FastAPI runs on localhost:8000 inside WSL
- Windows can access it via http://localhost:8000
- No manual port forwarding required for localhost usage

---

## Running the project

CLI:
python main.py

API:
uvicorn api:app --reload --port 8000

Test:
curl -X POST http://localhost:8000/deepthought-graph \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello deepthought"}'

---

## Operational rules (do not break reproducibility)

- Identity lives only in `Modelfile`
- Cognition lives only in `app/graph.py`
- Memory lives only in `app/memory_v2_clean.json` (or the configured MEMORY_FILE)
- Do not add system_prompt files
- Do not mutate the v1.1-stable tag
- All experiments go in `v1.1-dev`

---

## Troubleshooting

Ollama not responding:
- ollama serve
- ollama list
- ollama create deepthought -f Modelfile

WSL issues:
- If networking behaves oddly: wsl --shutdown
- Prefer repo in /home/<user>/... for performance
- If using /mnt/*, expect slower I/O for memory/log writes

Import errors:
- Ensure venv is activated
- pip install -r requirements.txt
- Run commands from repo root

API errors:
- Confirm uvicorn is running on port 8000
- Confirm route exists in api.py
- Confirm request JSON matches api.py expectations

---

# Internal documentation: cognitive graph (app/graph.py) — exact node flow (v1.1-dev)

This section documents the real execution flow as implemented in `app/graph.py`.

## Graph state contract

GraphState (TypedDict):
- input: str
- messages: List[Dict[str, Any]]
- output: Optional[str]
- route: Optional[str]
- memory: Dict[str, Any]
- memory_instruction: Optional[Dict[str, Any]]

## Memory subsystem

Memory file:
- MEMORY_FILE = "/mnt/e/agentic/app/memory_v2_clean.json" (current)

Memory schema (created if missing):
- short_term: []
- long_term: []
- profile: { user: {}, agent: {} }
- meta:
  - version: "2.0"
  - last_update
  - short_term_size
  - long_term_size

Persistence behavior:
- save_memory_state updates meta timestamps and sizes on every write.
- load_memory_state creates the file with default schema if missing.

## LLM subsystem

LLM:
- ChatOllama(model="qwen2.5:7b-instruct", temperature=0.0, num_ctx=8192)

Prompting:
- build_prompt_for_mode(mode, state) builds a single consolidated prompt.
- Includes:
  - LAYER_2_CONTRACT
  - LAYER_3_USER_MODEL
  - history from state["messages"]
- Special override:
  - If mode == "llm" and user input matches Phase 2-only triggers, returns a strict Phase 2 override prompt.

## Router subsystem

router_node routes based on keyword triggers (Spanish + English):
- command: ["comando", "cmd", "explica", "cómo funciona", "como funciona", "command", "explain"]
- summarizer: ["resumen", "resume", "resumir", "summary"]
- analysis: ["analiza", "análisis", "analisis", "evaluación", "evaluacion", "evalúa", "evalua", "analyze", "analysis", "evaluate"]
- memory_query: ["qué recuerdas", "que recuerdas", "qué sabes de mí", "que sabes de mi", "memoria", "memory"]
- default: llm

router_edge returns state["route"] for conditional edges.

## Node catalog (exact)

1) load_memory
- Reads memory from MEMORY_FILE.
- Sets:
  - state["memory"] = memory
  - state["messages"] = memory["short_term"].copy()
  - appends current user input as {"role":"human","content": state["input"]}

2) profile_initializer
- Ensures memory["profile"]["user"] exists.
- If already exists and non-empty: no changes.
- Writes memory to disk if initialization occurs.

3) router
- Sets state["route"] based on keyword triggers.

4) llm
- prompt = build_prompt_for_mode("llm", state)
- response = llm.invoke(prompt)
- Sets state["output"]
- Appends assistant message to state["messages"]

5) summarizer
- prompt = build_prompt_for_mode("summarizer", state)
- response = llm.invoke(prompt)
- Sets state["output"]
- Appends assistant message to state["messages"]

6) analysis
- prompt = build_prompt_for_mode("analysis", state)
- response = llm.invoke(prompt)
- Sets state["output"]
- Appends assistant message to state["messages"]

7) command
- prompt = build_prompt_for_mode("command", state)
- response = llm.invoke(prompt)
- Sets state["output"]
- Appends assistant message to state["messages"]

8) memory_query
- Reads memory["short_term"] last 20 messages.
- Produces a raw text dump:
  "Last 20 messages in short_term:\n\n" + joined messages
- Sets state["output"]
- Appends assistant message to state["messages"]

9) memory_manager
- LLM-based memory decision node.
- Builds a JSON-only prompt including:
  - Current memory (full JSON)
  - Recent messages (full JSON)
  - Mandatory output schema:
    {
      "action": "store_raw" | "store_summary" | "update_profile" | "ignore",
      "target": "short_term" | "long_term" | "profile" | "none",
      "payload": null | {...} | [{...}],
      "tags": ["string"],
      "importance": "low" | "medium" | "high",
      "reason": "string"
    }
- Parses response as JSON.
- On parse failure: fallback instruction = ignore/none.
- Sets state["memory_instruction"].

10) memory_writer
- Applies state["memory_instruction"] to memory and persists it.
- Behaviors:
  - store_raw + short_term + payload(list): memory["short_term"].extend(payload)
  - store_summary + long_term: appends entry:
    {
      "id": "ltm-###",
      "summary": payload,
      "timestamp": utc_iso,
      "tags": tags,
      "source": "memory_manager",
      "importance": importance
    }
  - update_profile + profile + payload(dict): merges sections into memory["profile"][section]
- Calls save_memory_state(memory)
- Updates state["memory"]

## Graph assembly (exact edges)

Entry point:
- load_memory

Linear pre-routing chain:
- load_memory → profile_initializer → router

Conditional routing:
- router --(route)--> one of:
  - llm
  - summarizer
  - analysis
  - command
  - memory_query

Post-route convergence:
- llm → memory_manager
- summarizer → memory_manager
- analysis → memory_manager
- command → memory_manager
- memory_query → memory_manager

Memory finalization:
- memory_manager → memory_writer → END

## Exact flow diagram (ASCII)
```
ENTRY
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
  +--> llm -----------+
  |                   |
  +--> summarizer ----|
  |                   |
  +--> analysis ------|--> memory_manager --> memory_writer --> END
  |                   |
  +--> command -------|
  |                   |
  +--> memory_query --+
```
## Determinism and side effects (exact)

Deterministic components:
- LLM temperature = 0.0
- Router keyword matching is deterministic.

Non-deterministic components (inherent):
- LLM outputs can still vary across model versions, runtime, or backend changes.

Side effects (writes):
- profile_initializer may write memory file.
- memory_writer always writes memory file.
- save_memory_state updates timestamps and sizes on every write.

WSL portability risk (current):
- MEMORY_FILE is hardcoded to /mnt/e/...
- Recommended to switch to repo-relative path for recovery on any PC.

---

## Roadmap

v1.1 — Deterministic cognitive graph (current)
v2.0 — Multi-agent swarm
v3.0 — Integrations and GUI

---

## About

AI Engineer | Agentic Systems Architect | LLM Orchestration | LangGraph & Ollama | Backend & Workflow Architecture | Open to Work

Contact:
Email: byron92m@gmail.com
GitHub: https://github.com/byron92m-stack
(Open to remote roles worldwide)
