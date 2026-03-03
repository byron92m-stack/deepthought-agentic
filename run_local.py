from agentic_system.graph import build_graph

graph = build_graph()

state = {
    "repo": "/mnt/e/agentic",
    "task": "Fix failing tests in auth module",
    "max_iterations": 5,
}

result = graph.invoke(state)
print(result)
