from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent


class SalesAgent(BaseAgent):
    """
    Agente de ventas: prospecta, redacta mensajes, analiza leads.
    """

    def handle(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}

        response_text = "SalesAgent ejecutó la tarea correctamente."

        return {
            "output": response_text,
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context,
        }
