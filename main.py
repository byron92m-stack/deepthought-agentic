from app.graph import get_graph

def main():
    graph = get_graph()

    print("deepthought – Full Cognitive Graph v1.1")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print("\n[stdin closed — exiting gracefully]")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("Exiting deepthought...")
            break

        state = {
            "input": user_input,
            "messages": [],  # ← limpio, el grafo lo llena correctamente
            "output": None,
            "route": None,
            "memory": {},
            "memory_instruction": None
        }

        try:
            result = graph.invoke(state)
            print(f"\ndeepthought: {result['output']}\n")
        except Exception as e:
            print(f"\n[ERROR] {e}\n")

if __name__ == "__main__":
    main()
