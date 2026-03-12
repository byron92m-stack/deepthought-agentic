# deepthought-agentic (v1.1)

Deterministic, modular agentic AI architecture for reproducible reasoning, explicit memory, and clean orchestration.
Designed for local execution using Ollama, a deterministic cognitive graph, and optional FastAPI exposure.

This repository is engineered so the entire system can be recovered from scratch on a new machine (Linux, WSL2, or macOS) with no hidden state, no legacy files, and no undocumented dependencies.

---

## What this project is

deepthought-agentic is a local cognitive-agent system built around three strictly separated layers:

1) Identity  
Defined only in `Modelfile`.  
This is the executive constitution of the agent: persona, constraints, and high-level reasoning posture.

2) Cognition  
Defined only in `app/graph.py`.  
This is the deterministic cognitive graph responsible for routing, reasoning, and memory I/O.

3) Exposure  
How the system is executed:
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
Additional local-only directories (not versioned, not required for recovery):
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
- Full auditability
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

Supported and tested environments:
- Linux (recommended)
- Windows + WSL2 (fully supported)
- macOS

No OS-specific code paths are used.

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

5) Create model:
ollama serve
ollama create deepthought -f Modelfile

---

## Windows + WSL2 setup (IMPORTANT)

This project runs **inside WSL**, not directly on Windows Python.

### WSL requirements
- Windows 10/11
- WSL2 enabled
- Ubuntu 22.04+ recommended

### Critical rules for WSL
- The project MUST live inside the Linux filesystem:
  /home/<user>/deepthought-agentic
- Do NOT run from /mnt/c or Windows paths
- Ollama must run inside WSL, not Windows

### Setup steps

1) Install WSL (from PowerShell):
wsl --install

2) Open Ubuntu (WSL terminal)

3) Install system dependencies:
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl git

4) Install Ollama inside WSL:
curl -fsSL https://ollama.com/install.sh | sh

5) Clone the repo:
git clone https://github.com/byron92m-stack/deepthought-agentic
cd deepthought-agentic
git checkout v1.1-stable

6) Python environment:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

7) Start Ollama and create model:
ollama serve
ollama create deepthought -f Modelfile

### Networking note (WSL)
- FastAPI runs on localhost:8000 inside WSL
- Windows browser can access it via http://localhost:8000
- No port forwarding required

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
- Memory lives only in `app/memory_v2_clean.json`
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
- Ensure you are not running from /mnt/c
- Ensure Ollama is running inside WSL
- Restart WSL if networking behaves oddly: wsl --shutdown

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
