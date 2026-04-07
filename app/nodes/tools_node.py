from typing import Dict, Any
from tools_registry import ejecutar_herramienta


def tools_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta una herramienta y escribe el resultado en el estado del grafo.
    """
    tool_name = state.get("tool_name")
    tool_args = state.get("tool_args", {})

    if not tool_name:
        output = "Error: no se proporcionó tool_name"
        state["output"] = output
        state["messages"].append({"role": "assistant", "content": output})
        return state

    try:
        result = ejecutar_herramienta(tool_name, **tool_args)
        output = f"[TOOL RESULT]\n{result}"
    except Exception as e:
        output = f"[TOOL ERROR]\n{str(e)}"

    # Guardar en el estado del grafo
    state["output"] = output
    state["messages"].append({"role": "assistant", "content": output})

    return state
