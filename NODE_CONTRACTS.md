# Deepthought — Node Contracts (v1.2)

## 1. Purpose of This Document
This document defines the formal contracts for every node in the deepthought cognitive graph.  
A node contract specifies:

- purpose,
- inputs,
- outputs,
- state usage,
- transition rules,
- constraints,
- failure modes.

These contracts ensure deterministic behavior and safe extensibility.

---

## 2. Node: load_memory

### Purpose
Load persistent memory and inject it into the graph state.

### Input
- `state` (empty or minimal)
- `user_input` (ignored)

### Output
- updated `state` containing:
  - messages,
  - profile,
  - system_state
- next node: `router`
- no user-facing message

### Constraints
- must not modify memory structure
- must not generate LLM output

### Failure Modes
- corrupted JSON → system must fallback to empty memory

---

## 3. Node: router

### Purpose
Select the correct agent based on user intent.

### Input
- `state`
- `user_input`

### Output
- next node: one of  
  `llm`, `analysis`, `summarizer`, `command`
- no user-facing message

### Constraints
- must return exactly one valid node
- must not call nodes directly
- must not modify memory

### Failure Modes
- ambiguous intent → fallback to `llm`

---

## 4. Node: llm

### Purpose
General-purpose reasoning and technical responses.

### Input
- `state`
- `user_input`

### Output
- `message`: technical explanation
- updated `state["last_output"]`
- next node: `router`

### Constraints
- must follow technical tone
- must not hallucinate structure
- must not modify memory directly

### Failure Modes
- overly long output → truncate in orchestrator

---

## 5. Node: analysis

### Purpose
Perform structured reasoning using a deterministic framework.

### Input
- `state`
- `user_input`

### Output
A structured message with:

1. Objective  
2. Problem  
3. Causes  
4. Risks  
5. Scenarios  
6. Recommendations  
7. Next Steps  

Next node: `router`

### Constraints
- must follow exact structure
- no creative writing
- no emotional tone

### Failure Modes
- missing sections → orchestrator logs warning

---

## 6. Node: summarizer

### Purpose
Produce an executive summary.

### Input
- `state`
- `user_input` or previous node output

### Output
- 3–5 bullet points
- next node: `router`

### Constraints
- no new information
- no interpretation

### Failure Modes
- too long → orchestrator truncates

---

## 7. Node: command

### Purpose
Explain technical commands or errors.

### Input
- `state`
- `user_input`

### Output
Structured explanation:

1. Command  
2. Component Breakdown  
3. Execution Behavior  
4. Risks  
5. Expected Output  

Next node: `router`

### Constraints
- no assumptions
- no alternative commands

### Failure Modes
- invalid command → return “unrecognized command”

---

## 8. Adding New Nodes (Contract Requirements)

A new node must define:

- purpose  
- input contract  
- output contract  
- state usage  
- transition rule  
- constraints  
- failure modes  

Document the node here before implementation.

