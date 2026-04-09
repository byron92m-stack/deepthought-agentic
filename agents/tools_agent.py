from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent


class ToolsAgent(BaseAgent):
    """
    Agente pasivo de coordinación de herramientas.
    En v2.0 no ejecuta tools directamente.
    """

    def handle(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {
            "output": "ToolsAgent no ejecuta herramientas directamente en v2.0.",
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context or {},
        }
