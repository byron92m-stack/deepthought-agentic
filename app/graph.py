from pathlib import Path
from typing import TypedDict, Optional

from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END


class GraphState(TypedDict):
    user_input: str
    analysis: Optional[str]


# Configura deepthought desde Ollama (usa el SYSTEM del Modelfile)
llm = ChatOllama(
    model="deepthought:latest",
    temperature=0.2,
    num_ctx=8192,
)

# Prompt minimalista: NO SYSTEM aquí (deepthought ya lo trae del modelo)
prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}")
])


def analysis_node(state: GraphState):
    """Nodo de análisis: deepthought produce análisis ejecutivo."""
    chain = prompt | llm
    result = chain.invoke({"input": state["user_input"]})
    return {"analysis": result.content}


def build_graph():
    """Construye el grafo cognitivo."""
    workflow = StateGraph(GraphState)

    workflow.add_node("analysis", analysis_node)
    workflow.set_entry_point("analysis")
    workflow.add_edge("analysis", END)

    return workflow.compile()
