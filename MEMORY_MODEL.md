# Deepthought — Memory Model (v1.1)

## 1. Purpose of the Memory System
Deepthought uses a persistent memory model to maintain continuity across sessions. Memory enables:

- long-term context retention,
- user profile persistence,
- stateful reasoning,
- reproducible behavior,
- auditability.

Memory is stored in:

```
memory_v2_clean.json
```

---

## 2. Memory Structure

### 2.1 Top-Level Fields
The memory file contains:

- **messages** — chronological conversation history.
- **profile** — persistent user identity and preferences.
- **system_state** — internal state of the graph.
- **metadata** — versioning and integrity fields.

---

## 3. Message Model

Each message entry contains:

- `role` — `human` or `assistant`.
- `content` — full text of the message.
- `timestamp` — ISO timestamp.
- `node` — which agent produced the message.
- `context_window` — optional context snapshot.

Example:

```json
{
  "role": "assistant",
  "content": "1. Objective: Respond to user greeting...",
  "timestamp": "2026-03-20T14:06:00",
  "node": "llm"
}
```

---

## 4. Profile Model

The profile stores long-term user information:

- name,
- preferences,
- system settings,
- persistent traits.

Example:

```json
{
  "name": "Byron",
  "language": "es",
  "style": "technical"
}
```

The profile is loaded once at startup and reused.

---

## 5. System State Model

Tracks:

- last node executed,
- pending tasks,
- internal flags,
- memory version.

This ensures deterministic graph execution.

---

## 6. Memory Lifecycle

### 6.1 Load Phase
At startup:

1. `memory_v2_clean.json` is read.
2. Messages are injected into graph state.
3. Profile is loaded.
4. System state is restored.

Log evidence:

```
Memory loaded correctly
profile.user already exists, not modified.
```

### 6.2 Update Phase
After each interaction:

- new messages are appended,
- system state is updated,
- profile may be modified.

### 6.3 Save Phase
Memory is written back to disk:

```
MEMORY SAVED — 20 mensajes guardados
```

---

## 7. Memory Integrity Rules

- Memory must always be valid JSON.
- Only the orchestrator may write to memory.
- Nodes must not mutate memory directly.
- Memory must not exceed the context window limit.
- Corrupted memory must trigger a reset.

---

## 8. Memory Reset Procedure

If memory becomes corrupted:

1. Backup the file.
2. Create a new empty structure:
```json
{
  "messages": [],
  "profile": {},
  "system_state": {}
}
```
3. Restart deepthought.

---

## 9. Extending the Memory Model

To add new fields:

1. Add schema changes to the orchestrator.
2. Update load/save logic.
3. Document the new field here.
4. Ensure backward compatibility.

---

## 10. Verified Status

Memory is fully operational:

- loads correctly,
- saves correctly,
- integrates with the graph,
- persists across sessions.

