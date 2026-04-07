from typing import Dict, Any
from tools_registry import ejecutar_herramienta


def tools_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta una herramienta y escribe el resultado en el estado del grafo.
    Contrato esperado:
    state = {
        "messages": [...],
        "tool_call": {
            "name": str,
            "args": dict
        }
    }
    """

    tool_call = state.get("tool_call")

    if not tool_call:
        output = "Error: no se proporcionó tool_call"
    else:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})

        if not tool_name:
            output = "Error: no se proporcionó tool_name"
        else:
            try:
                result = ejecutar_herramienta(tool_name, **tool_args)
                output = f"[TOOL RESULT]\n{result}"
            except Exception as e:
                output = f"[TOOL ERROR]\n{str(e)}"

    # Asegurar estructura mínima del estado
    state.setdefault("messages", []).append(
        {"role": "assistant", "content": output}
    )
    state["output"] = output

    return state
