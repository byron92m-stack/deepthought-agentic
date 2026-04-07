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
from pathlib import Path
from app.nodes.tools_node import tools_node
from app.tool_contracts import TOOL_SCHEMAS

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_FILE = BASE_DIR / "memory_v2_clean.json"

console = Console()

# ------------------------------------------------------------------
# PROMPTS DIRECTORY + LOADER (v1.3 híbrido)
# ------------------------------------------------------------------
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

def load_prompt(name: str) -> str:
    """
    Loads an external prompt template from app/prompts/{name}.txt
    """
    path = PROMPTS_DIR / f"{name}.txt"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


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
    tool_name: Optional[str]
    tool_args: Optional[Dict[str, Any]]


# ------------------------------------------------------------------
# HYBRID MEMORY CONFIG (H1)
# ------------------------------------------------------------------
MAX_SHORT_TERM = 40  # límite determinista de short_term


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


def _deterministic_chunk_summary(messages: List[Dict[str, Any]]) -> str:
    """
    Resumen determinista (sin LLM): concatena mensajes recortando longitud.
    Mantiene trazabilidad sin depender del modelo.
    """
    lines = [f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in messages]
    text = "\n".join(lines)
    max_len = 2000
    if len(text) > max_len:
        text = text[:max_len] + "\n...[trimmed]..."
    return text


def apply_trimming(memory: Dict[str, Any]) -> None:
    """
    Trimming determinista:
    - Si short_term excede MAX_SHORT_TERM:
      - Mueve el overflow a long_term como resumen determinista.
      - Conserva solo los últimos MAX_SHORT_TERM en short_term.
    """
    short = memory.get("short_term", [])
    if len(short) <= MAX_SHORT_TERM:
        return

    overflow = short[:-MAX_SHORT_TERM]
    summary_text = _deterministic_chunk_summary(overflow)

    entry = {
        "id": f"ltm-{len(memory.get('long_term', [])) + 1:03d}",
        "summary": summary_text,
        "timestamp": datetime.utcnow().isoformat(),
        "tags": ["auto_trim"],
        "source": "deterministic_trimmer",
        "importance": "medium",
    }

    if "long_term" not in memory:
        memory["long_term"] = []
    memory["long_term"].append(entry)

    memory["short_term"] = short[-MAX_SHORT_TERM:]


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
   When the user does not request a specific format AND Layer 1 does not impose a different structure, deepthought MAY use the following operational lens:
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
   - deepthought does not improvise outside the operational framework WHEN compatible with Layer 1.
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
    model="deepthought",
    temperature=0.0,
    num_ctx=32768,  # ajustar a 131072 si usas 128k
)
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])


def _history(messages: List[Dict[str, Any]]) -> str:
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages])


# ------------------------------------------------------------------
# build_prompt_for_mode — LAYERED, NON-OVERRIDING
# ------------------------------------------------------------------
def build_prompt_for_mode(mode: str, state: GraphState) -> str:
    history = _history(state["messages"])

    # Shared layered context (Layer 2 + Layer 3 as CONTEXT, not rules)
    context = (
        "Context — Layer 2 (Operational Contract):\n"
        + LAYER_2_CONTRACT
        + "\n\n"
        "Context — Layer 3 (User Model):\n"
        + LAYER_3_USER_MODEL
        + "\n\n"
    )

    # LLM mode (default)
    if mode == "llm":
        return (
            context
            + "Previous context:\n"
            + history
            + "\n\nUser instruction:\n"
            + state["input"]
        )

    # Summarizer mode (external prompt, layered)
    if mode == "summarizer":
        template = load_prompt("summarizer")
        return (
            context
            + template
                .replace("{history}", history)
                .replace("{input}", state["input"])
        )

    # Analysis mode (no identity override, no hard format imposition)
    if mode == "analysis":
        return (
            context
            + "Analysis request:\n"
            + state["input"]
            + "\n\nContext:\n"
            + history
        )

    # Command explanation mode (still contextual, no role override)
    if mode == "command":
        return (
            context
            + "Command explanation request:\n"
            + state["input"]
        )

    # Fallback
    return context + "Instruction:\n" + state["input"]


# ------------------------------------------------------------------
# GRAPH NODES
# ------------------------------------------------------------------
def load_memory(state: GraphState) -> GraphState:
    memory = load_memory_state()
    state["memory"] = memory

    # Cargar short_term SIN inyectar el input actual
    state["messages"] = memory.get("short_term", []).copy()

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
    text = state["input"].strip()

    # --- DETECCIÓN DE TOOL-CALLING ---
    # Formato mínimo: tool: nombre argumento1=valor argumento2=valor
    if text.lower().startswith("tool:"):
        state["route"] = "tool"
        return state

    # --- RUTAS EXISTENTES ---
    lower = text.lower()
    if any(k in lower for k in ["comando", "cmd", "explica", "cómo funciona", "command", "explain"]):
        route = "command"
    elif any(k in lower for k in ["resumen", "resume", "resumir", "summary"]):
        route = "summarizer"
    elif any(k in lower for k in ["analiza", "análisis", "analysis", "evaluate"]):
        route = "analysis"
    elif any(k in lower for k in ["qué recuerdas", "que recuerdas", "memoria", "memory"]):
        route = "memory_query"
    else:
        route = "llm"

    state["route"] = route
    return state


def parse_tool_command(text: str) -> Dict[str, Any]:
    """
    Formato mínimo:
    tool: nombre arg1=valor arg2=valor
    """
    text = text.replace("tool:", "").strip()
    parts = text.split()

    tool_name = parts[0]
    args = {}

    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            args[k] = v

    return {"tool_name": tool_name, "tool_args": args}


def tool_parser_node(state: GraphState) -> GraphState:
    """
    Nodo que interpreta el comando 'tool:' del input
    y rellena state["tool_name"] y state["tool_args"].
    """
    parsed = parse_tool_command(state["input"])

    state["tool_name"] = parsed.get("tool_name")
    state["tool_args"] = parsed.get("tool_args", {})

    log(
        "TOOL PARSER",
        f"tool_name={state['tool_name']}, tool_args={state['tool_args']}"
    )

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
You are the Reduced Memory Manager of deepthought.

Objective:
- Classify the recent interaction with tags and importance.
- Optionally update the user profile.
- You DO NOT decide storage. Storage is deterministic and handled by the system.

Strict rules:
- Respond ONLY with a valid JSON object.
- Do NOT add any text outside the JSON.
- Do NOT explain your decisions.
- Do NOT repeat the recent messages.

Current profile:
{json.dumps(memory.get("profile", {}), indent=2, ensure_ascii=False)}

Recent messages (last 10):
{json.dumps(messages[-10:], indent=2, ensure_ascii=False)}

Mandatory output schema:
{{
  "action": "update_profile" | "ignore",
  "payload": null | {{...}},
  "tags": ["string"],
  "importance": "low" | "medium" | "high"
}}
"""
    log("MEMORY MANAGER PROMPT (REDUCED)", prompt_text)
    response = llm.invoke(prompt_text)

    try:
        instruction = json.loads(response.content)
    except Exception:
        instruction = {
            "action": "ignore",
            "payload": None,
            "tags": [],
            "importance": "medium",
        }

    state["memory_instruction"] = instruction
    return state


def memory_writer_node(state: GraphState) -> GraphState:
    memory = state["memory"]
    instr = state.get("memory_instruction") or {}

    action = instr.get("action")
    payload = instr.get("payload")

    # Sincronizar short_term con mensajes actuales
    memory["short_term"] = state["messages"].copy()

    # Actualizar perfil si corresponde
    if action == "update_profile" and isinstance(payload, dict):
        if "profile" not in memory:
            memory["profile"] = {"user": {}, "agent": {}}
        for section, data in payload.items():
            if section not in memory["profile"]:
                memory["profile"][section] = {}
            if isinstance(data, dict):
                memory["profile"][section].update(data)

    apply_trimming(memory)
    save_memory_state(memory)

    state["memory"] = memory
    return state


# ------------------------------------------------------------------
# GRAPH ASSEMBLY (EXTENDED WITH TOOL PARSER + TOOL EXECUTOR NODE)
# ------------------------------------------------------------------
def get_graph():
    graph = StateGraph(GraphState)

    # -------------------------
    # NODOS EXISTENTES
    # -------------------------
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

    # -------------------------
    # NUEVOS NODOS
    # -------------------------
    graph.add_node("tool_parser", tool_parser_node)
    graph.add_node("tool_executor", tools_node)   # <--- NOMBRE CORREGIDO

    # -------------------------
    # ENTRY POINT
    # -------------------------
    graph.set_entry_point("load_memory")
    graph.add_edge("load_memory", "profile_initializer")
    graph.add_edge("profile_initializer", "router")

    # -------------------------
    # ROUTER EXTENDIDO
    # -------------------------
    graph.add_conditional_edges(
        "router",
        router_edge,
        {
            "llm": "llm",
            "summarizer": "summarizer",
            "analysis": "analysis",
            "command": "command",
            "memory_query": "memory_query",
            "tool": "tool_parser",   # <--- RUTA A PARSER
        },
    )

    # -------------------------
    # PARSER → TOOL EXECUTOR
    # -------------------------
    graph.add_edge("tool_parser", "tool_executor")

    # -------------------------
    # POST-PROCESAMIENTO
    # -------------------------
    # SOLO los nodos de conversación pasan por memory_manager
    for node in [
        "llm",
        "summarizer",
        "analysis",
        "command",
        "memory_query",
    ]:
        graph.add_edge(node, "memory_manager")

    # Las herramientas NO pasan por memory_manager
    graph.add_edge("tool_executor", END)

    graph.add_edge("memory_manager", "memory_writer")
    graph.add_edge("memory_writer", END)

    return graph.compile()
