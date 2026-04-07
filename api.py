from fastapi import FastAPI
from pydantic import BaseModel
from app.graph import get_graph

app = FastAPI(title="deepthought – Full Cognitive Graph v1.1")

graph = get_graph()

class Query(BaseModel):
    input: str

@app.post("/deepthought-graph")
def run_graph(query: Query):
    state = {
        "input": query.input,
        "messages": [],
        "output": None,
    }

    final_state = graph.invoke(state)

    return {
        "response": final_state["output"]
    }
