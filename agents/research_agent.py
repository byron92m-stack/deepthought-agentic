from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """
    Agente de investigación y análisis.
    """

    def handle(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}

        response_text = "ResearchAgent ejecutó la tarea correctamente."

        return {
            "output": response_text,
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context,
        }
