from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """
    Clase base para todos los agentes.
    Define la interfaz mínima y el contrato común.
    """

    def __init__(
        self,
        name: str,
        role: str,
        prompt: str,
        contract: Dict[str, Any],
    ) -> None:
        self.name = name
        self.role = role
        self.prompt = prompt
        self.contract = contract

    @abstractmethod
    def handle(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Punto de entrada principal del agente.
        Siempre debe devolver un dict estructurado.
        """
        raise NotImplementedError

    def get_metadata(self) -> Dict[str, Any]:
        """
        Información básica del agente para el orquestador.
        """
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": self.contract.get("capabilities", []),
            "inputs": self.contract.get("inputs", []),
            "outputs": self.contract.get("outputs", []),
        }
