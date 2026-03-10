from app.graph import get_graph

def main():
    graph = get_graph()

    print("deepthought – Full Cognitive Graph v1.1")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye.")
            break

        state = {
            "input": user_input,
            "messages": [],
            "output": None,
        }

        result = graph.invoke(state)
        print("\ndeepthought:", result["output"], "\n")


if __name__ == "__main__":
    main()
