# Deepthought — System Design Document (v1.1)

## 1. Design Philosophy

Deepthought is designed as a deterministic cognitive graph rather than a monolithic LLM wrapper. The system prioritizes:

- **Modularity** — each cognitive function is isolated in a node.
- **Determinism** — the router selects agents based on explicit rules.
- **Transparency** — every step is logged and auditable.
- **Extensibility** — new nodes and agents can be added without breaking the system.
- **Persistence** — memory and profile survive across sessions.
- **Offline operation** — the system runs fully local using a Modelfile-defined LLM.

This design ensures reproducibility, auditability, and controlled cognitive behavior.

---

## 2. Core Components

### 2.1 Orchestrator (`main.py`)
The orchestrator is responsible for:

- loading persistent memory,
- initializing the user profile,
- instantiating the cognitive graph,
- running the interactive loop,
- delegating execution to the router,
- saving memory after each interaction.

It acts as the runtime supervisor.

---

## 3. Cognitive Graph Architecture

The cognitive graph is defined in `app/graph.py`. It is a directed graph where each node represents a cognitive function.

### 3.1 Node Types

- **load_memory** — injects persistent memory into graph state.
- **router** — determines which agent should handle the input.
- **llm** — general-purpose reasoning and technical responses.
- **analysis** — structured reasoning (problem, causes, risks, scenarios, recommendations).
- **summarizer** — executive summaries.
- **command** — technical command explanations.

Each node has:
- a purpose,
- a prompt template,
- an expected output format,
- a transition rule.

---

## 4. Router Design

The router is the central decision-making component. It evaluates:

- user intent,
- linguistic patterns,
- memory context,
- system state.

It selects one of the agents based on deterministic rules. This prevents hallucinations and ensures predictable behavior.

### Router responsibilities:
- classify intent,
- select the correct node,
- enforce cognitive discipline,
- prevent invalid transitions.

---

## 5. Memory System

### 5.1 Persistent Memory (`memory_v2_clean.json`)
Stores:
- conversation history,
- user profile,
- system state.

Memory is:
- loaded at startup,
- injected into graph state,
- updated after each interaction,
- saved automatically.

### 5.2 Profile
A persistent `profile.user` file stores long-term identity and preferences.

---

## 6. Logging System

### 6.1 Interactive logs (`runs/`)
Each session produces:
- input,
- selected route,
- node transitions,
- outputs,
- errors (if any).

### 6.2 API logs (`api_runs/`)
Same structure, but for API calls.

Logs enable:
- debugging,
- reproducibility,
- auditing,
- regression testing.

---

## 7. API Layer (`api.py`)

The API exposes the cognitive graph through a REST interface.

Example:

```bash
curl -X POST http://localhost:8000/deepthought-graph \
-H "Content-Type: application/json" \
-d '{"input": "hello"}'
```

The API executes the same graph as interactive mode.

---

## 8. Local LLM Runtime

The `Modelfile` defines:
- model path,
- inference parameters,
- runtime configuration.

This ensures:
- offline operation,
- reproducible inference,
- consistent behavior across sessions.

---

## 9. Internal Data Flow

### 9.1 High-level flow

```
User Input
    ↓
main.py (orchestrator)
    ↓
load_memory
    ↓
router
    ↓
selected agent (llm / analysis / summarizer / command)
    ↓
output
    ↓
memory update
    ↓
logging
    ↓
return to user
```

### 9.2 State propagation
Each node receives:
- the current graph state,
- the user input,
- the memory context.

Each node returns:
- updated state,
- output,
- next node.

---

## 10. Design Constraints

- The graph must remain deterministic.
- Memory must never be mutated outside the orchestrator.
- Router rules must be explicit and auditable.
- Nodes must not call each other directly.
- All transitions must be defined in the graph.

---

## 11. Extensibility Guidelines

### 11.1 Adding a new node
1. Create a new function in `app/graph.py`.
2. Define:
   - purpose,
   - prompt template,
   - expected output,
   - transition rule.
3. Register the node in the graph.
4. Update the router if needed.

### 11.2 Adding a new agent
Agents are specialized nodes. Requirements:
- clear purpose,
- deterministic output format,
- minimal overlap with existing agents.

### 11.3 Modifying the router
Router changes must:
- be explicit,
- be documented,
- not break existing transitions.

---

## 12. Risks and Limitations

- Router misclassification can lead to incorrect agent selection.
- Memory corruption can affect reasoning.
- Adding nodes without clear contracts can destabilize the graph.
- Overlapping agent responsibilities can cause ambiguity.

---

## 13. Evolution Roadmap

### v1.2
- modularize prompts,
- add validation layer for node outputs,
- improve router heuristics.

### v1.3
- introduce tool-use nodes,
- add structured memory segments.

### v2.0
- multi-agent orchestration,
- external tool integration,
- distributed graph execution.

---

## 14. Status (Verified)

- Graph functional.
- Router operational.
- Memory stable.
- API available.
- Logs clean.
- VHDX is the single source of truth.

