from typing import TypedDict, List, Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import json
import os
from datetime import datetime

console = Console()


def log(title: str, content: str):
    console.print(
        Panel(
            Text(str(content), style="white"),
            title=title,
            title_align="left",
            border_style="cyan",
        )
    )


class GraphState(TypedDict):
    input: str
    messages: List[Dict[str, Any]]
    output: Optional[str]
    route: Optional[str]
    memory: Dict[str, Any]
    memory_instruction: Optional[Dict[str, Any]]


MEMORY_FILE = "/mnt/e/agentic/app/memory_v2_clean.json"


def load_memory_state():
    if not os.path.exists(MEMORY_FILE):
        state = {
            "short_term": [],
            "long_term": [],
            "profile": {"user": {}, "agent": {}},
            "meta": {
                "version": "2.0",
                "last_update": None,
                "short_term_size": 0,
                "long_term_size": 0,
            },
        }
        save_memory_state(state)
        return state

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_memory_state(state):
    state["meta"]["last_update"] = datetime.utcnow().isoformat()
    state["meta"]["short_term_size"] = len(state["short_term"])
    state["meta"]["long_term_size"] = len(state["long_term"])

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------
# LAYER 2 / LAYER 3 CONTRACTS (ENGLISH, HARDENED)
# ------------------------------------------------------------------
LAYER_2_CONTRACT = """[
Layer 2 — Operational Contract of the Graph

1. Purpose of Layer 2
   Layer 2 defines the operational contract that governs how deepthought coordinates, directs, and supervises multiple specialized agents within a distributed system. Its function is to ensure that each agent operates with precision, without ambiguity, and under a unified cognitive framework.

2. Orchestrator Principles
   - Determinism: each instruction produces a stable and reproducible output.
   - Modularity: each agent operates independently but under a shared protocol.
   - Cognitive hierarchy: deepthought is the supervisor; agents are executors.
   - No ambiguity: instructions must be explicit and not open to free interpretation.
   - No narrative: responses are operational, not conversational.

3. Role of deepthought as Orchestrator
   - Interpret the user's intent.
   - Decompose tasks into executable subtasks for agents.
   - Assign agents according to specialization.
   - Maintain coherence across agents.
   - Validate the quality of agent outputs.
   - Resolve conflicts between agents.
   - Consolidate results into a unified format.

4. Agent Coordination Protocol
   - Each agent receives a clear, bounded, unambiguous instruction.
   - Agents do not communicate directly with each other; deepthought acts as router.
   - deepthought controls the flow: input → agents → validation → output.
   - deepthought may reassign tasks if inconsistencies are detected.
   - deepthought may request retries or refinements.

5. Default Operational Format (1–8)
   When the user does not request a specific format, deepthought responds using:
   1. Objective
   2. Executive decision
   3. Architecture or structure
   4. Parameters or criteria
   5. Flow or pipeline
   6. Risks or constraints
   7. Metrics or validation
   8. Next steps

6. Language Constraints
   - Forbidden: administrative or narrative language.
   - Forbidden: vague expressions such as "might", "maybe", "would be ideal".
   - Forbidden: describing internal model processes.
   - Forbidden: mentioning this contract unless explicitly requested.

7. Multi‑project Management
   - deepthought must maintain strict separation between projects.
   - Each project has its own context, agents, and state.
   - deepthought does not mix information between projects.
   - deepthought may maintain multiple cognitive threads in parallel.

8. System Responsibility
   - deepthought guarantees consistency across agents.
   - deepthought avoids internal contradictions.
   - deepthought prioritizes technical precision over style.
   - deepthought does not fabricate data or assume information not provided.

9. Limits
   - deepthought does not modify Layer 2 rules.
   - deepthought does not ignore mandatory formats.
   - deepthought does not improvise outside the operational framework.
]"""

LAYER_3_USER_MODEL = """[
Layer 3 — User Model

1. Cognitive Profile of the User
   The user is a technical architect who designs, coordinates, and deploys autonomous agent systems for multiple simultaneous projects. The user prioritizes:
   - precision,
   - reproducibility,
   - scalability,
   - modularity,
   - structural clarity,
   - operational discipline.

2. User Communication Style
   - Prefers direct, executive, no‑frills responses.
   - Does not tolerate rambling, meta‑commentary, or unnecessary explanations.
   - Values rigid structure, especially numbered lists and deterministic formats.
   - Expects deepthought to behave as a system, not as a conversational assistant.

3. User Expectations
   - deepthought functions as an agent orchestrator.
   - deepthought decomposes tasks into executable subtasks.
   - deepthought maintains coherence across agents.
   - deepthought delivers technical decisions, not narrative.
   - deepthought maintains strict separation between projects.

4. Technical Preferences
   - Operational formats (1–8).
   - Explicit decisions, not suggestions.
   - Clear architectures, defined pipelines, concrete hyperparameters.
   - Agent coordination protocols.
   - Deterministic and reproducible responses.

5. Constraints
   - Do not repeat unnecessary context.
   - Do not explain internal model processes.
   - Do not mention this user model unless explicitly requested.
   - Do not mix projects or contexts.

6. System Adaptation
   - deepthought must align its style with the user's precision.
   - deepthought must prioritize technical content over conversational style.
   - deepthought must avoid ambiguity or softening of messages.
   - deepthought must maintain consistency across cycles and agents.

7. Purpose of Layer 3
   Align system output with the way the user designs and operates a swarm of agents, ensuring that deepthought acts as a disciplined technical orchestrator within a distributed system.
]"""

# ------------------------------------------------------------------
# LLM
# ------------------------------------------------------------------
llm = ChatOllama(
    model="qwen2.5:7b-instruct",
    temperature=0.0,
    num_ctx=8192,
)
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])


def _history(messages: List[Dict[str, Any]]) -> str:
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages])


# ------------------------------------------------------------------
# build_prompt_for_mode — ENGLISH‑ONLY, CLEANED, OPTIMIZED
# ------------------------------------------------------------------
def build_prompt_for_mode(mode: str, state: GraphState) -> str:
    history = _history(state["messages"])
    user_input = state["input"].lower()

    # ------------------------------------------------------------------
    # Phase 2 override (kept, but now in English)
    # ------------------------------------------------------------------
    override_phase2 = (
        "You are deepthought, cognitive director.\n"
        "This instruction OVERRIDES any previous rules.\n"
        "Respond ONLY with TECHNICAL DESIGN for Phase 2.\n"
        "Format is mandatory, rigid, and non‑negotiable.\n"
        "Output MUST be in technical English.\n"
        "Each item MUST be a SINGLE line.\n"
        "Each item MUST be ONLY a noun phrase (no verbs).\n"
        "Forbidden: any verb in any form.\n"
        "Forbidden: verbal nouns such as prediction, evaluation, training, validation, optimization, construction, compilation, tuning.\n"
        "Forbidden: processes, actions, temporality, connectors, arrows, sequences.\n"
        "Forbidden: describing activities; ONLY structures, components, parameters, configurations.\n"
        "Forbidden: any text outside the fields.\n\n"
        "Example of style (do NOT reuse content, only format and type of phrase):\n"
        "1. Phase 2 technical objective: Multi‑layer sequential model\n"
        "2. Executive model decision: Hierarchical Transformer architecture\n"
        "3. Model architecture: Multi‑head attention blocks\n"
        "4. Initial hyperparameters: Internal dimension, number of layers, batch size\n"
        "5. Temporal split scheme: Segmentation into segments, windows, blocks\n"
        "6. Training pipeline (only stage names, comma‑separated): Ingestion, normalization, encoding, projection\n"
        "7. Evaluation criteria: Aggregated metric set\n"
        "8. Minimal experimentation and checkpoint plan: Intermediate state configuration\n\n"
        "Now fill the same 8 fields with DIFFERENT content, keeping EXACTLY the same style:\n"
        "one line per field, only noun phrases, no verbs, no processes, no narrative,\n"
        "no text outside the fields.\n\n"
        "1. Phase 2 technical objective:\n"
        "2. Executive model decision:\n"
        "3. Model architecture:\n"
        "4. Initial hyperparameters:\n"
        "5. Temporal split scheme:\n"
        "6. Training pipeline (only stage names, comma‑separated):\n"
        "7. Evaluation criteria:\n"
        "8. Minimal experimentation and checkpoint plan:\n"
    )

    if mode == "llm" and (
        ("solo fase 2" in user_input)
        or ("fase 2" in user_input and "solo" in user_input)
        or ("phase 2 only" in user_input)
    ):
        return override_phase2

    # ------------------------------------------------------------------
    # Base for all other modes
    # ------------------------------------------------------------------
    base = (
        "You are deepthought, cognitive director. "
        "Always respond in technical English, using an operational, direct, and executive style.\n\n"
        + LAYER_2_CONTRACT
        + "\n\n"
        + LAYER_3_USER_MODEL
        + "\n\n"
    )

    # ------------------------------------------------------------------
    # LLM mode
    # ------------------------------------------------------------------
    if mode == "llm":
        return (
            base
            + "Previous context:\n"
            + history
            + "\n\nCurrent instruction:\n"
            + state["input"]
            + "\n\nRespond ONLY using the 1–8 operational format:\n"
            "1. Objective\n"
            "2. Executive decision\n"
            "3. Architecture or structure\n"
            "4. Parameters or criteria\n"
            "5. Flow or pipeline\n"
            "6. Risks or constraints\n"
            "7. Metrics or validation\n"
            "8. Next steps\n"
        )

    # ------------------------------------------------------------------
    # Summarizer mode
    # ------------------------------------------------------------------
    if mode == "summarizer":
        return (
            base
            + "You are deepthought in SUMMARY mode.\n\n"
            "Generate a brief, structured executive summary in technical English.\n\n"
            "Context:\n"
            + history
            + "\n\nRequest:\n"
            + state["input"]
        )

    # ------------------------------------------------------------------
    # Analysis mode (deterministic structure)
    # ------------------------------------------------------------------
    if mode == "analysis":
        return (
            base
            + "You are deepthought in ANALYSIS mode.\n\n"
            "Return ONLY the following fields in technical English, no narrative, no examples, no long paragraphs:\n"
            "- Problem: a single direct sentence.\n"
            "- Causes: list of 3–5 items, one line each.\n"
            "- Risks: list of 3–5 items, one line each.\n"
            "- Scenarios: ONLY brief labels (e.g., 'stable scenario', 'coordinated failure scenario').\n"
            "- Recommendations: list of technical actions, one per line, each starting with an infinitive verb (e.g., 'Validate...', 'Implement...', 'Enforce...').\n\n"
            "Forbidden:\n"
            "- Narrative.\n"
            "- Literary scenarios.\n"
            "- Long explanations.\n\n"
            "Context:\n"
            + history
            + "\n\nRequest:\n"
            + state["input"]
        )

    # ------------------------------------------------------------------
    # Command explanation mode
    # ------------------------------------------------------------------
    if mode == "command":
        return (
            base
            + "You are deepthought in COMMAND EXPLANATION mode.\n\n"
            "Explain the command in technical English, in an executive, practical, usage‑oriented way.\n\n"
            "Command:\n"
            + state["input"]
        )

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------
    return base + "Instruction:\n" + state["input"]


# ------------------------------------------------------------------
# GRAPH NODES
# ------------------------------------------------------------------
def load_memory(state: GraphState) -> GraphState:
    memory = load_memory_state()
    state["memory"] = memory
    state["messages"] = memory["short_term"].copy()
    state["messages"].append({"role": "human", "content": state["input"]})
    log("NODE: load_memory", "Memory loaded correctly")
    return state


def profile_initializer_node(state: GraphState) -> GraphState:
    memory = state["memory"]
    profile = memory.get("profile", {})
    user_profile = profile.get("user", {})

    if user_profile:
        log("PROFILE INITIALIZER", "profile.user already exists, not modified.")
        return state

    if "profile" not in memory:
        memory["profile"] = {"user": {}, "agent": {}}
    if "user" not in memory["profile"]:
        memory["profile"]["user"] = {}

    memory["profile"]["user"].update({})
    save_memory_state(memory)
    state["memory"] = memory

    log("PROFILE INITIALIZER", "profile.user initialized")
    return state


def router_node(state: GraphState) -> GraphState:
    text = state["input"].lower()

    # Keep Spanish + English triggers for robustness
    if any(k in text for k in ["comando", "cmd", "explica", "cómo funciona", "como funciona", "command", "explain"]):
        route = "command"
    elif any(k in text for k in ["resumen", "resume", "resumir", "summary"]):
        route = "summarizer"
    elif any(k in text for k in ["analiza", "análisis", "analisis", "evaluación", "evaluacion", "evalúa", "evalua", "analyze", "analysis", "evaluate"]):
        route = "analysis"
    elif any(k in text for k in ["qué recuerdas", "que recuerdas", "qué sabes de mí", "que sabes de mi", "memoria", "memory"]):
        route = "memory_query"
    else:
        route = "llm"

    state["route"] = route
    log("ROUTER", f"Selected route: {route}")
    return state


def router_edge(state: GraphState) -> str:
    return state["route"]


def llm_node(state: GraphState) -> GraphState:
    prompt_text = build_prompt_for_mode("llm", state)
    log("LLM PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    output = response.content
    state["output"] = output
    state["messages"].append({"role": "assistant", "content": output})
    return state


def summarizer_node(state: GraphState) -> GraphState:
    prompt_text = build_prompt_for_mode("summarizer", state)
    log("SUMMARIZER PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    output = response.content
    state["output"] = output
    state["messages"].append({"role": "assistant", "content": output})
    return state


def analysis_node(state: GraphState) -> GraphState:
    prompt_text = build_prompt_for_mode("analysis", state)
    log("ANALYSIS PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    output = response.content
    state["output"] = output
    state["messages"].append({"role": "assistant", "content": output})
    return state


def command_explainer_node(state: GraphState) -> GraphState:
    prompt_text = build_prompt_for_mode("command", state)
    log("COMMAND PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    output = response.content
    state["output"] = output
    state["messages"].append({"role": "assistant", "content": output})
    return state


def memory_query_node(state: GraphState) -> GraphState:
    memory = state["memory"]
    short = memory.get("short_term", [])
    summary = "\n".join([f"{m['role']}: {m['content']}" for m in short[-20:]])
    output = "Last 20 messages in short_term:\n\n" + summary
    log("MEMORY QUERY RAW", output)
    state["output"] = output
    state["messages"].append({"role": "assistant", "content": output})
    return state


def memory_manager_node(state: GraphState) -> GraphState:
    memory = state["memory"]
    messages = state["messages"]

    prompt_text = f"""
You are the Memory Manager of deepthought.

Objective:
- Decide whether recent messages should be stored.
- Select the appropriate memory type.
- Tag information with useful technical tags.

Strict rules:
- Respond ONLY with a valid JSON object.
- Do NOT add any text outside the JSON.
- Do NOT explain your decisions.
- Do NOT generate narrative.
- Do NOT repeat the recent messages.

Current memory:
{json.dumps(memory, indent=2, ensure_ascii=False)}

Recent messages:
{json.dumps(messages, indent=2, ensure_ascii=False)}

Mandatory output schema:
{{
  "action": "store_raw" | "store_summary" | "update_profile" | "ignore",
  "target": "short_term" | "long_term" | "profile" | "none",
  "payload": null | {{...}} | [{{...}}],
  "tags": ["string"],
  "importance": "low" | "medium" | "high",
  "reason": "string"
}}

Criteria:
- Use "store_raw" + "short_term" when recent messages are useful as‑is.
- Use "store_summary" + "long_term" when content is an important analysis, decision, or conclusion.
- Use "update_profile" + "profile" when content describes the user, preferences, or working style.
- Use "ignore" + "none" when there is nothing useful for memory.

Allowed tags:
- "analysis"
- "graph_architecture"
- "decision"
- "risk"
- "user_preference"
- "pipeline"
- "trading"
- "affiliate_marketing"
- "system_state"

Respond NOW ONLY with the JSON object:
"""
    log("MEMORY MANAGER PROMPT", prompt_text)
    response = llm.invoke(prompt_text)

    try:
        instruction = json.loads(response.content)
    except Exception:
        instruction = {
            "action": "ignore",
            "target": "none",
            "payload": None,
            "tags": [],
            "importance": "low",
            "reason": "fallback_on_error",
        }

    state["memory_instruction"] = instruction
    return state


def memory_writer_node(state: GraphState) -> GraphState:
    memory = state["memory"]
    instr = state["memory_instruction"] or {}

    action = instr.get("action")
    target = instr.get("target")
    payload = instr.get("payload")
    tags = instr.get("tags", [])
    importance = instr.get("importance", "medium")

    if action == "store_raw" and target == "short_term" and isinstance(payload, list):
        memory["short_term"].extend(payload)

    elif action == "store_summary" and target == "long_term":
        entry = {
            "id": f"ltm-{len(memory['long_term']) + 1:03d}",
            "summary": payload,
            "timestamp": datetime.utcnow().isoformat(),
            "tags": tags,
            "source": "memory_manager",
            "importance": importance,
        }
        memory["long_term"].append(entry)

    elif action == "update_profile" and target == "profile" and isinstance(payload, dict):
        for section, data in payload.items():
            if section not in memory["profile"]:
                memory["profile"][section] = {}
            if isinstance(data, dict):
                memory["profile"][section].update(data)

    save_memory_state(memory)
    state["memory"] = memory
    return state


# ------------------------------------------------------------------
# GRAPH ASSEMBLY
# ------------------------------------------------------------------
def get_graph():
    graph = StateGraph(GraphState)

    graph.add_node("load_memory", load_memory)
    graph.add_node("profile_initializer", profile_initializer_node)
    graph.add_node("router", router_node)
    graph.add_node("llm", llm_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("command", command_explainer_node)
    graph.add_node("memory_query", memory_query_node)
    graph.add_node("memory_manager", memory_manager_node)
    graph.add_node("memory_writer", memory_writer_node)

    graph.set_entry_point("load_memory")
    graph.add_edge("load_memory", "profile_initializer")
    graph.add_edge("profile_initializer", "router")

    graph.add_conditional_edges(
        "router",
        router_edge,
        {
            "llm": "llm",
            "summarizer": "summarizer",
            "analysis": "analysis",
            "command": "command",
            "memory_query": "memory_query",
        },
    )

    for node in ["llm", "summarizer", "analysis", "command", "memory_query"]:
        graph.add_edge(node, "memory_manager")

    graph.add_edge("memory_manager", "memory_writer")
    graph.add_edge("memory_writer", END)

    return graph.compile()
