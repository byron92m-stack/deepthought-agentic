DeepThought — Memory Model (v2.0)

------------------------------------------------------------
1. Purpose of the Memory System

DeepThought v2.0 uses an explicit, deterministic memory model to maintain continuity,
auditability, and reproducibility across sessions.

Memory enables:
- short-term conversational continuity,
- long-term contextual retention,
- stable user/system profiling,
- deterministic routing and execution,
- full auditability and recovery.

Memory is stored in:

memory_v2_clean.json

This file is the authoritative baseline for recovery.

------------------------------------------------------------
2. Memory Architecture (v2.0)

Memory in v2.0 is hybrid and segmented. It is not a monolithic log.

The memory system is composed of:
- short_term memory
- long_term memory
- profile memory
- memory metadata

Memory is:
- loaded explicitly at startup,
- managed deterministically,
- persisted explicitly,
- never mutated implicitly by agents or nodes.

------------------------------------------------------------
3. Memory Structure

3.1 Top-Level Fields

The memory file contains the following top-level fields:

- messages  
  Canonical conversation history (sanitized).

- profile  
  Persistent user/system profile.

- memory_meta  
  Metadata describing memory versioning and state.

No other top-level fields are allowed in the v2.0 baseline.

------------------------------------------------------------
4. Message Model

Each message entry represents a user-visible interaction.

Required fields:
- role        — "human" or "assistant"
- content     — full text content
- timestamp   — ISO 8601 timestamp
- source      — node or agent that produced the message

Optional fields:
- agent       — agent name (if produced by an agent)
- route       — routing path taken
- context_id  — optional execution context identifier

Example:

{
  "role": "assistant",
  "content": "ResearchAgent recibió la tarea. Modo stub activo.",
  "timestamp": "2026-04-08T21:07:13",
  "source": "agent_executor",
  "agent": "research_agent"
}

------------------------------------------------------------
5. Profile Model (Layer 3)

The profile stores stable user/system information.

Typical fields:
- user.name
- user.language
- user.preferences
- system.version
- system.constraints

Example:

{
  "user": {
    "name": "Byron",
    "language": "es",
    "style": "technical"
  },
  "system": {
    "version": "2.0"
  }
}

Profile rules:
- Loaded once at startup.
- Must not be overwritten if already present.
- May only be modified explicitly by authorized logic.
- Treated as read-only by agents.

------------------------------------------------------------
6. Memory Metadata (memory_meta)

memory_meta tracks the internal state of memory management.

Typical fields:
- version
- last_update
- short_term_size
- long_term_size

Example:

{
  "version": "2.0",
  "last_update": "2026-04-08T21:07:13.721754",
  "short_term_size": 8,
  "long_term_size": 0
}

memory_meta is maintained exclusively by memory_manager.

------------------------------------------------------------
7. Memory Lifecycle

7.1 Load Phase

At startup:
1) memory_v2_clean.json is read.
2) Memory is validated and sanitized.
3) Messages are injected into graph state.
4) Profile is initialized (if missing).
5) memory_meta is loaded or initialized.

Log evidence:
- "Memory loaded correctly"
- "profile.user already exists, not modified."

------------------------------------------------------------

7.2 Update Phase

After each user-visible output:
- new messages are appended to state,
- no memory is persisted yet,
- agents and nodes do not mutate memory directly.

------------------------------------------------------------

7.3 Management Phase (memory_manager)

memory_manager:
- applies deterministic trimming rules,
- enforces segmentation (short_term / long_term),
- sanitizes invalid entries,
- updates memory_meta.

No LLM is used for trimming or summarization.

------------------------------------------------------------

7.4 Save Phase (memory_writer)

memory_writer:
- persists memory explicitly to disk,
- logs success or failure,
- does not modify memory content.

Example log:
- "MEMORY SAVED — 8 mensajes guardados"

------------------------------------------------------------
8. Memory Integrity Rules

- Memory must always be valid JSON.
- Memory must conform to the v2.0 schema.
- Only memory_manager may modify memory content.
- Only memory_writer may persist memory.
- Agents must never mutate memory directly.
- Router must never mutate memory.
- Corrupted memory must be sanitized, not trusted.

------------------------------------------------------------
9. Memory Reset Procedure

If memory becomes corrupted:

1) Backup memory_v2_clean.json.
2) Create a minimal valid structure:

{
  "messages": [],
  "profile": {},
  "memory_meta": {
    "version": "2.0",
    "short_term_size": 0,
    "long_term_size": 0
  }
}

3) Restart DeepThought.

------------------------------------------------------------
10. Extending the Memory Model

To extend memory safely:

1) Update the memory schema explicitly.
2) Update load and validation logic.
3) Update memory_manager rules.
4) Document the change in this file.
5) Preserve backward compatibility where possible.

------------------------------------------------------------
11. Determinism Guarantees

The memory system guarantees:
- deterministic load behavior,
- deterministic trimming,
- deterministic persistence,
- reproducible recovery,
- full auditability.

------------------------------------------------------------
12. Verified Status (v2.0)

Memory is fully operational:
- loads correctly,
- managed deterministically,
- persists correctly,
- integrates with multi-agent routing,
- survives restarts,
- supports full recovery.

------------------------------------------------------------
13. Stability Notice

This document reflects the system state as of v2.0-stable.

The following elements are considered frozen for the v2.0 baseline:
- memory schema
- memory lifecycle
- memory_manager + memory_writer responsibilities
- deterministic trimming policy

Any future changes must be evaluated against this baseline.
