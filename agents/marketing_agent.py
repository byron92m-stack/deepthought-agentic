from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent


class MarketingAgent(BaseAgent):
    """
    Agente de marketing: contenido, campañas, copywriting.
    """

    def handle(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}

        response_text = "MarketingAgent ejecutó la tarea correctamente."

        return {
            "output": response_text,
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context,
        }
