DeepThought — Node Contracts (v1.1)

1. Purpose of This Document

This document defines the formal contracts for every node in the DeepThought cognitive graph.

A node contract specifies:
- purpose
- inputs
- outputs
- state usage
- transition rules
- constraints
- failure modes

These contracts ensure deterministic behavior, auditability, and safe extensibility.
Any implementation that violates these contracts is considered invalid.

------------------------------------------------------------

2. Node: load_memory

Purpose:
Load persistent memory and inject it into the graph state.

Input:
- state (empty or minimal)
- user_input (ignored)

Output:
Updated state containing:
- messages
- profile
- system_state

Next node: router
No user-facing message.

Constraints:
- Must not modify memory structure
- Must not generate LLM output

Failure Modes:
- Corrupted JSON → system must fallback to empty memory

------------------------------------------------------------

3. Node: router

Purpose:
Select the correct cognitive path based on user intent.

Input:
- state
- user_input

Output:
Next node: one of
- llm
- analysis
- summarizer
- command
- tools

No user-facing message.

Constraints:
- Must return exactly one valid node
- Must not call nodes directly
- Must not modify memory

Failure Modes:
- Ambiguous intent → fallback to llm

------------------------------------------------------------

4. Node: llm

Purpose:
General-purpose reasoning and technical responses.

Input:
- state
- user_input

Output:
- Assistant message appended to state["messages"]
- Updated state["last_output"]

Next node: router

Constraints:
- Must follow technical tone
- Must not hallucinate system structure
- Must not modify memory directly

Failure Modes:
- Overly long output → truncated by orchestrator

------------------------------------------------------------

5. Node: analysis

Purpose:
Perform structured reasoning using a deterministic framework.

Input:
- state
- user_input

Output:
A structured message with:
1. Objective
2. Problem
3. Causes
4. Risks
5. Scenarios
6. Recommendations
7. Next Steps

Next node: router

Constraints:
- Must follow exact structure
- No creative writing
- No emotional tone

Failure Modes:
- Missing sections → orchestrator logs warning

------------------------------------------------------------

6. Node: summarizer

Purpose:
Produce an executive summary of prior output.

Input:
- state
- user_input or previous node output

Output:
- 3–5 bullet points appended to state["messages"]

Next node: router

Constraints:
- No new information
- No interpretation

Failure Modes:
- Output too long → truncated

------------------------------------------------------------

7. Node: command

Purpose:
Explain technical commands or errors.

Input:
- state
- user_input

Output:
Structured explanation:
1. Command
2. Component Breakdown
3. Execution Behavior
4. Risks
5. Expected Output

Next node: router

Constraints:
- No assumptions
- No alternative commands

Failure Modes:
- Invalid command → return “unrecognized command”

------------------------------------------------------------

8. Node: tools

Purpose:
Execute a concrete tool action under strict orchestration control.

Input:
State containing:
- messages (list)
- tool_call object:
  - name (string)
  - args (dict)

Example state:
state = {
    "messages": [...],
    "tool_call": {
        "name": "leer_archivo",
        "args": {"path": "data/test.txt"}
    }
}

Output:
- Tool execution result appended to state["messages"]
- Raw output stored in state["output"]

Next node: router

Constraints:
- Tools must only be executed through this node
- Direct tool invocation is forbidden
- The node must not perform reasoning
- The node must not modify memory

Failure Modes:
- Missing tool_call → return error message
- Missing tool_call.name → return error message
- Tool execution error → return formatted tool error

------------------------------------------------------------

9. Adding New Nodes (Contract Requirements)

Any new node must define:
- purpose
- input contract
- output contract
- state usage
- transition rule
- constraints
- failure modes

The contract must be documented here before implementation.

------------------------------------------------------------

Stability Notice

This document reflects the system state as of v1.1-stable.

The following elements are considered frozen:
- Graph structure
- Node contracts
- Tool invocation via tool_call
- Memory handling
- Router decision flow

Any future changes must be evaluated against this baseline.
