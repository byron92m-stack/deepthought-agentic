from app.nodes.tools_node import tools_node

def probar(tool_name, tool_args):
    state = {
        "tool_name": tool_name,
        "tool_args": tool_args,
    }
    result = tools_node(state)
    print(f"\n=== {tool_name} ===")
    print("state_in:", state)
    print("state_out:", result)

def main():
    # 1) Probar leer_archivo (asegúrate de que exista data/test.txt)
    probar("leer_archivo", {"path": "data/test.txt"})

    # 2) Probar listar_archivos
    probar("listar_archivos", {"directorio": "data"})

    # 3) Probar crear_tarea
    probar("crear_tarea", {"descripcion": "Tarea desde tools_node"})

    # 4) Probar calcular_balance
    probar("calcular_balance", {})

if __name__ == "__main__":
    main()
