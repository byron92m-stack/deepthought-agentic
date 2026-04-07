# Deepthought — Development Guide (v1.2)

## 1. Purpose of This Guide
This guide explains how to safely extend, modify, and evolve the deepthought cognitive graph. It provides the rules, workflows, and constraints required to maintain system stability while adding new capabilities.

This document applies to version **v1.2** and forward.

---

## 2. Development Principles

Deepthought follows these engineering principles:

- **Determinism** — every node must behave predictably.
- **Modularity** — each cognitive function lives in its own node.
- **Router-first discipline** — all execution must pass through the router.
- **Explicit contracts** — each node must define inputs, outputs, and transitions.
- **Backward compatibility** — new nodes must not break existing flows.
- **Auditability** — all reasoning must be traceable through logs.

These principles ensure that the system remains stable as it grows.

---

## 3. How to Add a New Node

### 3.1 Node Requirements
Every node must define:

- **Purpose** — what cognitive function it performs.
- **Prompt template** — deterministic instructions for the LLM.
- **Expected output** — structure and constraints.
- **Transition rule** — what node comes next.
- **State usage** — what parts of memory or context it reads.

### 3.2 Steps to Add a Node

1. Open `app/graph.py`.
2. Create a new function:

```python
def node_newcapability(state, user_input):
    """
    Purpose: Describe what this node does.
    Input: state, user_input
    Output: updated state, next node, message
    """
    prompt = f"""
    You are deepthought. Perform the following task:
    {user_input}
    """
    response = llm(prompt)
    state["last_output"] = response
    return state, "router", response
```

3. Register the node in the graph dictionary:

```python
graph["newcapability"] = node_newcapability
```

4. Add routing logic in the router (see Router Rules).
5. Document the node in `NODE_CONTRACTS.md` (optional but recommended).
6. Test the node interactively.
7. Validate logs in `runs/`.

---

## 4. How to Modify the Router

### 4.1 Rules for Router Changes

- Router rules must be **deterministic**.
- No overlapping conditions.
- No probabilistic or fuzzy routing.
- Router must always return a valid node.
- Router must not call nodes directly; it returns the node name.

### 4.2 Adding a New Routing Rule

Inside the router:

```python
if "translate" in user_input.lower():
    return "translator"
```

Rules must be:

- explicit,
- auditable,
- documented in `ROUTER_RULES.md`.

---

## 5. How to Add a New Agent Type

Agents are specialized nodes with strict cognitive roles.

### Requirements:

- clear purpose,
- unique cognitive function,
- deterministic output format,
- no overlap with existing agents.

### Example: Adding a “planner” agent

1. Create `node_planner`.
2. Add routing rule for planning tasks.
3. Document in ROUTER_RULES.md.
4. Add contract in NODE_CONTRACTS.md.
5. Test with:

```
python main.py
```

---

## 6. How to Modify Memory Behavior

Memory must remain:

- valid JSON,
- deterministic,
- controlled by the orchestrator.

### Allowed modifications:

- adding new fields,
- adding new metadata,
- adding new system state keys.

### Forbidden modifications:

- nodes writing directly to memory,
- nodes mutating memory structure,
- router modifying memory.

All memory changes must go through:

```python
save_memory()
```

Document changes in `MEMORY_MODEL.md`.

---

## 7. Versioning the System

### v1.2 versioning rules:

- All new nodes must be documented.
- Router changes must be logged.
- Memory schema changes must be versioned.
- Backward compatibility must be preserved.

### Version bump triggers:

- new node type,
- new agent,
- new memory field,
- new router rule,
- new API endpoint.

---

## 8. Testing and Validation

### 8.1 Manual Testing

Run:

```
python main.py
```

Test:

- greetings,
- analysis,
- summarization,
- commands,
- new nodes,
- router transitions.

### 8.2 Log Validation

Check:

```
runs/
api_runs/
```

Ensure:

- correct node selection,
- correct transitions,
- no recursion,
- no invalid nodes.

---

## 9. Safe Development Workflow

1. Create a new branch or copy of the project.
2. Add or modify nodes.
3. Update router rules.
4. Update documentation.
5. Test interactively.
6. Validate logs.
7. Merge into main version.

---

## 10. Roadmap for v1.3 and v2.0

### v1.3
- modular prompt templates,
- validation layer for node outputs,
- improved router heuristics.

### v2.0
- multi-agent orchestration,
- external tool integration,
- distributed graph execution,
- dynamic node loading.

---

## 11. Verified Status

Deepthought v1.2 is ready for:

- new nodes,
- new agents,
- router extensions,
- memory schema evolution.

This guide ensures safe and stable development.

