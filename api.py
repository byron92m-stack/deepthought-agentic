from fastapi import FastAPI
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI()
graph = build_graph()

class Query(BaseModel):
    user_input: str

@app.post("/deepthought-graph")
def run_graph(query: Query):
    state = {
        "user_input": query.user_input,
        "analysis": None,
    }
    result = graph.invoke(state)
    return result
