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
from agents.research_agent import ResearchAgent
from agents.finance_agent import FinanceAgent
from agents.marketing_agent import MarketingAgent
from agents.sales_agent import SalesAgent
from agents.support_agent import SupportAgent
from agents.tools_agent import ToolsAgent

AGENT_REGISTRY = {
    "research": ResearchAgent,
    "finance": FinanceAgent,
    "marketing": MarketingAgent,
    "sales": SalesAgent,
    "support": SupportAgent,
    "tools": ToolsAgent,
}

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

    # --- MULTI-AGENT STATE ---
    active_agent: Optional[str]
    agent_output: Optional[Dict[str, Any]]

    # --- MEMORY ---
    memory: Dict[str, Any]
    memory_instruction: Optional[Dict[str, Any]]

    # --- TOOLS ---
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


def _history(messages: List[Dict[str, Any]]) -> str:
    return "\n".join([f"{m['role']}: {m['content']}" for m in messages])


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
    text = state["input"].strip().lower()

    if text.startswith("tool:"):
        state["route"] = "tool"
    else:
        state["route"] = "agent"

    return state


def agent_router_node(state: GraphState) -> GraphState:
    text = state["input"].lower()

    if any(k in text for k in ["investiga", "research", "analiza mercado"]):
        agent = "research"
    elif any(k in text for k in ["finanzas", "precio", "coste", "roi"]):
        agent = "finance"
    elif any(k in text for k in ["marketing", "campaña", "branding"]):
        agent = "marketing"
    elif any(k in text for k in ["ventas", "sales", "pipeline"]):
        agent = "sales"
    else:
        agent = "support"

    state["active_agent"] = agent
    log("AGENT ROUTER", f"Selected agent: {agent}")
    return state


def agent_executor_node(state: GraphState) -> GraphState:
    agent_name = state.get("active_agent")

    if not agent_name or agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Invalid agent selected: {agent_name}")

    AgentClass = AGENT_REGISTRY[agent_name]

    # --- LOAD PROMPT (ROOT /agents/prompts) ---
    prompt_path = BASE_DIR / "agents" / "prompts" / f"{agent_name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()

    # --- LOAD CONTRACT (ROOT /agents/contracts) ---
    contract_path = BASE_DIR / "agents" / "contracts" / f"{agent_name}.json"
    if not contract_path.exists():
        raise FileNotFoundError(f"Contract not found: {contract_path}")

    with open(contract_path, "r", encoding="utf-8") as f:
        contract = json.load(f)

    # --- INSTANTIATE AGENT ---
    agent = AgentClass(
        name=agent_name,
        role=contract.get("role", ""),
        prompt=prompt,
        contract=contract,
    )

    # --- EXECUTE AGENT ---
    result = agent.handle(
        task=state["input"],
        context={
            "memory": state["memory"],
            "messages": state["messages"],
        },
    )

    # --- WRITE BACK TO STATE ---
    state["agent_output"] = result
    state["output"] = result.get("output", "")

    state["messages"].append({
        "role": agent_name,
        "content": state["output"],
    })

    log("AGENT EXECUTOR", f"Agent '{agent_name}' executed successfully")
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


def validate_tool_call(tool_name: str, tool_args: Dict[str, Any]) -> None:
    if tool_name not in TOOL_SCHEMAS:
        raise ValueError(f"Tool '{tool_name}' is not registered")

    schema = TOOL_SCHEMAS[tool_name]
    required = schema.get("required_args", [])

    for arg in required:
        if arg not in tool_args:
            raise ValueError(f"Missing required arg '{arg}' for tool '{tool_name}'")


def tool_parser_node(state: GraphState) -> GraphState:
    """
    Nodo que interpreta el comando 'tool:' del input
    y rellena state["tool_name"] y state["tool_args"].
    Valida el tool contra TOOL_SCHEMAS antes de ejecutar.
    """
    parsed = parse_tool_command(state["input"])

    state["tool_name"] = parsed.get("tool_name")
    state["tool_args"] = parsed.get("tool_args", {})

    # --- HARD VALIDATION ---
    validate_tool_call(state["tool_name"], state["tool_args"])

    log(
        "TOOL PARSER",
        f"tool_name={state['tool_name']}, tool_args={state['tool_args']}"
    )

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

    # --- CORE NODES ---
    graph.add_node("load_memory", load_memory)
    graph.add_node("profile_initializer", profile_initializer_node)
    graph.add_node("router", router_node)

    # --- AGENT FLOW ---
    graph.add_node("agent_router", agent_router_node)
    graph.add_node("agent_executor", agent_executor_node)

    # --- TOOL FLOW ---
    graph.add_node("tool_parser", tool_parser_node)
    graph.add_node("tool_executor", tools_node)

    # --- MEMORY FLOW ---
    graph.add_node("memory_manager", memory_manager_node)
    graph.add_node("memory_writer", memory_writer_node)

    # --- ENTRY POINT ---
    graph.set_entry_point("load_memory")

    # --- INITIAL FLOW ---
    graph.add_edge("load_memory", "profile_initializer")
    graph.add_edge("profile_initializer", "router")

    # --- ROUTING (INLINE, NO router_edge) ---
    graph.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "agent": "agent_router",
            "tool": "tool_parser",
        },
    )

    # --- AGENT PATH ---
    graph.add_edge("agent_router", "agent_executor")
    graph.add_edge("agent_executor", "memory_manager")
    graph.add_edge("memory_manager", "memory_writer")
    graph.add_edge("memory_writer", END)

    # --- TOOL PATH ---
    graph.add_edge("tool_parser", "tool_executor")
    graph.add_edge("tool_executor", END)

    return graph.compile()
