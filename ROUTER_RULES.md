# Deepthought — Router Rules (v1.1)

## 1. Purpose of the Router
The router is the central decision-making component of the cognitive graph. Its role is to analyze user input, evaluate context, and select the correct agent (node) to handle the request. The router ensures deterministic, predictable behavior and prevents ambiguous or overlapping cognitive actions.

---

## 2. Router Responsibilities
- Classify user intent.
- Select the appropriate cognitive agent.
- Enforce deterministic transitions.
- Prevent invalid or ambiguous node execution.
- Maintain cognitive discipline across the graph.
- Ensure that each node receives the correct type of input.

---

## 3. Router Inputs
The router evaluates four sources of information:

### 3.1 User Input
- keywords,
- linguistic patterns,
- command-like structures,
- question types,
- tone and intent.

### 3.2 Memory Context
- recent conversation history,
- user profile,
- system state.

### 3.3 Graph State
- previous node,
- pending tasks,
- unresolved outputs.

### 3.4 System Rules
- explicit routing rules defined in `graph.py`.

---

## 4. Routing Logic

### 4.1 Agent Selection Rules

#### **Rule: analysis**
Triggered when input requires structured reasoning:
- “analyze…”
- “explain the problem…”
- “what are the risks…”
- “give me scenarios…”
- “root cause…”

#### **Rule: summarizer**
Triggered when input requests condensation:
- “summarize…”
- “give me a short version…”
- “executive summary…”

#### **Rule: command**
Triggered when input references:
- shell commands,
- code,
- technical instructions,
- CLI usage,
- file paths.

Examples:
- “what does this command do?”
- “explain this error”
- “how do I run…”

#### **Rule: llm**
Default fallback for:
- greetings,
- general questions,
- open-ended prompts,
- conversational input.

#### **Rule: load_memory**
Executed only at startup.

---

## 5. Deterministic Priority Order
When multiple rules match, the router applies this priority:

1. **command**  
2. **analysis**  
3. **summarizer**  
4. **llm**

This prevents ambiguity and ensures consistent behavior.

---

## 6. Invalid Transitions
The router prevents:
- loops between nodes,
- recursive agent calls,
- transitions that bypass the router,
- nodes calling each other directly.

All transitions must return to the router unless explicitly defined.

---

## 7. Output Contract
Each agent must return:
- a structured output,
- a clear message,
- no side effects outside its scope.

The router validates:
- output format,
- completeness,
- next node.

---

## 8. Extending Router Rules
To add a new rule:

1. Define a new agent node.
2. Add a routing condition in `graph.py`.
3. Ensure the rule is deterministic.
4. Document the rule in this file.
5. Validate that no existing rule overlaps.

---

## 9. Router Stability Guarantees
- deterministic selection,
- reproducible behavior,
- no hidden heuristics,
- no probabilistic routing,
- no agent overlap.

---

## 10. Verified Status
The router is fully operational and validated through logs:

```
Selected route: llm
Selected route: analysis
Selected route: summarizer
Selected route: command
```

