from typing import TypedDict, List, Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import json
import os

# Logging
console = Console()

def log(title: str, content: str):
    console.print(
        Panel(
            Text(content, style="white"),
            title=title,
            title_align="left",
            border_style="cyan"
        )
    )

# Estado del grafo
class GraphState(TypedDict):
    input: str
    messages: List[Dict[str, Any]]
    output: Optional[str]
    route: Optional[str]

# Memoria persistente (v2 limpia)
MEMORY_FILE = "/mnt/e/agentic/app/memory_v2_clean.json"
MEMORY: List[Dict[str, str]] = []

def load_memory_from_disk():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    MEMORY.extend(data)
                    log("MEMORY LOADED",
                        f"{len(MEMORY)} mensajes cargados")
        except Exception as e:
            log("ERROR", f"No se pudo cargar memory_v2_clean.json: {e}")
    else:
        log("MEMORY", "No existe memory_v2_clean.json")

def save_memory_to_disk():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(MEMORY, f, indent=2, ensure_ascii=False)
        log("MEMORY SAVED",
            f"{len(MEMORY)} mensajes guardados")
    except Exception as e:
        log("ERROR", f"No se pudo guardar memory_v2_clean.json: {e}")

load_memory_from_disk()

# Modelo
llm = ChatOllama(
    model="deepthought:latest",
    temperature=0.2,
    num_ctx=8192
)

prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])

# Nodo load_memory
def load_memory(state: GraphState) -> GraphState:
    log("NODE: load_memory",
        f"Cargando memoria — {len(MEMORY)} mensajes")
    state["messages"] = MEMORY.copy()
    return state

# Router v2.1
def router_node(state: GraphState) -> GraphState:
    text = state["input"].lower()

    if any(k in text for k in
           ["comando", "cmd", "explica",
            "como funciona", "que hace"]):
        route = "command"

    elif any(k in text for k in
             ["resumen", "resume",
              "resumir", "summary"]):
        route = "summarizer"

    elif any(k in text for k in
             ["analiza", "analisis",
              "evaluacion", "evalua"]):
        route = "analysis"

    elif any(k in text for k in
             ["que recuerdas", "que sabes de mi",
              "memoria"]):
        route = "memory_query"

    else:
        route = "llm"

    state["route"] = route
    log("ROUTER", f"Ruta elegida: {route}")
    return state

def router_edge(state: GraphState) -> str:
    return state["route"]

# Utilidad de historial
def _history(messages):
    return "\n".join(
        [f"{m['role']}: {m['content']}" for m in messages]
    )

# Nodos especializados
def llm_node(state: GraphState) -> GraphState:
    prompt_text = (
        _history(state["messages"]) +
        "\nhuman: " + state["input"]
    )
    log("LLM PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    state["output"] = response.content
    return state

def summarizer_node(state: GraphState) -> GraphState:
    prompt_text = (
        "Eres un agente que resume.\n\n"
        "Contexto:\n" +
        _history(state["messages"]) +
        "\n\nPedido:\n" +
        state["input"]
    )
    log("SUMMARIZER PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    state["output"] = response.content
    return state

def analysis_node(state: GraphState) -> GraphState:
    prompt_text = (
        "Eres un agente analista.\n\n"
        "Devuelve:\n"
        "- Problema\n"
        "- Causas\n"
        "- Riesgos\n"
        "- Escenarios\n"
        "- Recomendaciones\n\n"
        "Contexto:\n" +
        _history(state["messages"]) +
        "\n\nPedido:\n" +
        state["input"]
    )
    log("ANALYSIS PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    state["output"] = response.content
    return state

def command_explainer_node(state: GraphState) -> GraphState:
    prompt_text = (
        "Eres un agente que explica comandos.\n\n"
        "Comando:\n" +
        state["input"]
    )
    log("COMMAND PROMPT", prompt_text)
    response = llm.invoke(prompt_text)
    state["output"] = response.content
    return state

def memory_query_node(state: GraphState) -> GraphState:
    summary = "\n".join(
        [f"{m['role']}: {m['content']}" for m in MEMORY[-20:]]
    )

    output = (
        "Últimos 20 mensajes guardados en memoria:\n\n"
        f"{summary}"
    )

    log("MEMORY QUERY RAW", output)
    state["output"] = output
    return state

# Guardado de memoria (sin introspección)
def save_memory(state: GraphState) -> GraphState:
    if state["route"] == "memory_query":
        return state

    MEMORY.append({"role": "human", "content": state["input"]})
    MEMORY.append({"role": "assistant", "content": state["output"]})
    save_memory_to_disk()
    return state

# Grafo v2.1
def get_graph():
    graph = StateGraph(GraphState)

    graph.add_node("load_memory", load_memory)
    graph.add_node("router", router_node)
    graph.add_node("llm", llm_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("command", command_explainer_node)
    graph.add_node("memory_query", memory_query_node)
    graph.add_node("save_memory", save_memory)

    graph.set_entry_point("load_memory")
    graph.add_edge("load_memory", "router")

    graph.add_conditional_edges(
        "router",
        router_edge,
        {
            "llm": "llm",
            "summarizer": "summarizer",
            "analysis": "analysis",
            "command": "command",
            "memory_query": "memory_query"
        }
    )

    graph.add_edge("llm", "save_memory")
    graph.add_edge("summarizer", "save_memory")
    graph.add_edge("analysis", "save_memory")
    graph.add_edge("command", "save_memory")
    graph.add_edge("memory_query", "save_memory")

    graph.add_edge("save_memory", END)

    return graph.compile()
