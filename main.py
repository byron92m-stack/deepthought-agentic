from fastapi import FastAPI
from pydantic import BaseModel

from app.graph import build_graph

graph_app = build_graph()
app = FastAPI()


class Query(BaseModel):
    input: str


@app.post("/analyze")
def analyze(query: Query):
    state = {
        "user_input": query.input,
        "analysis": None,
    }

    final_state = graph_app.invoke(state)
    return {
        "analysis": final_state["analysis"],
    }
