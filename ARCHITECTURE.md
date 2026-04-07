# Deepthought — Cognitive Graph Architecture (v1.1)

## 1. Overview
Deepthought is a local cognitive graph system running inside WSL2. It combines a modular graph architecture, a task router, persistent memory, and a local LLM defined through a Modelfile. The system operates fully offline and is executed from:

```
/home/nw/deepthought
```

This directory is the single source of truth.

---

## 2. Project Structure

```
deepthought/
├── Modelfile
├── README.md
├── api.py
├── api_runs/
├── app/
│   ├── __init__.py
│   └── graph.py
├── main.py
├── memory_v2_clean.json
├── requirements.txt
├── runs/
└── venv/
```

### Component roles

- **main.py** — Orchestrator and interactive loop.
- **app/graph.py** — Cognitive graph definition, nodes, router, and agent logic.
- **memory_v2_clean.json** — Persistent memory store.
- **api.py** — Optional REST API interface.
- **api_runs/** — Logs for API executions.
- **runs/** — Logs for interactive executions.
- **venv/** — Isolated Python environment.
- **Modelfile** — Local LLM configuration.

---

## 3. Execution Flow

### 3.1 Startup sequence
1. Load persistent memory.
2. Initialize user profile.
3. Initialize cognitive graph.
4. Enter interactive loop or API mode.

### 3.2 Interaction cycle
1. User sends input.
2. Router analyzes intent.
3. Router selects an agent.
4. Agent executes its specialized prompt.
5. Output is returned.
6. Memory is updated and saved.
7. Logs are written to `runs/` or `api_runs/`.

---

## 4. Cognitive Graph

The graph is defined in `app/graph.py`. It contains:

### 4.1 Nodes
- **load_memory** — Loads memory into graph state.
- **router** — Selects the appropriate agent.
- **llm** — General-purpose technical responses.
- **analysis** — Structured reasoning (problem, causes, risks, scenarios, recommendations).
- **summarizer** — Executive summaries.
- **command** — Technical command explanations.

### 4.2 Router
The router evaluates:
- user intent,
- linguistic patterns,
- memory context,
- system state.

It then selects one of the agents above.

---

## 5. Memory System

### 5.1 Persistent memory
Stored in:

```
memory_v2_clean.json
```

Memory is:
- loaded at startup,
- injected into graph state,
- updated after each interaction,
- saved automatically.

### 5.2 Profile
A persistent profile file (`profile.user`) is created on first run and reused.

---

## 6. Logging System

### 6.1 Interactive logs
Stored in:

```
runs/
```

### 6.2 API logs
Stored in:

```
api_runs/
```

Logs include:
- input,
- selected route,
- node transitions,
- outputs,
- errors (if any).

---

## 7. API Layer

`api.py` exposes the cognitive graph through a REST interface.

Example request:

```bash
curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'
```

The API executes the same graph as the interactive mode.

---

## 8. Local LLM Configuration

The `Modelfile` defines:
- model path,
- inference parameters,
- runtime configuration.

This enables fully offline operation.

---

## 9. Environment

Deepthought runs inside a Python 3.12 virtual environment:

```
venv/
```

Dependencies are defined in:

```
requirements.txt
```

---

## 10. Architecture Diagram

```
                ┌────────────────────┐
                │      main.py       │
                │  Orchestrator      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   load_memory      │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │      router        │
                └─────────┬──────────┘
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌────────────┐     ┌────────────┐     ┌────────────┐
│    llm     │     │  analysis  │     │ summarizer │
└────────────┘     └────────────┘     └────────────┘
        │                  │                  │
        └──────────┬──────┴──────┬───────────┘
                   ▼             ▼
            ┌────────────┐  ┌────────────┐
            │  command    │  │   other    │
            └────────────┘  └────────────┘
```

---

## 11. System Status (Verified)

- Graph functional.
- Router operational.
- Memory loading and saving correctly.
- API available.
- No duplicate directories.
- No broken paths.
- VHDX is the single source of truth.

---

## 12. Maintenance Notes

- `runs/` and `api_runs/` can be safely cleared.
- `venv/` should not be deleted.
- `memory_v2_clean.json` must remain in project root.
- `app/graph.py` is the core of the cognitive system.

