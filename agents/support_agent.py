import json
from pathlib import Path
from typing import Any, Dict, Optional

from agents.base_agent import BaseAgent


BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
CONTRACTS_DIR = BASE_DIR / "contracts"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class SupportAgent(BaseAgent):
    """
    Agente de soporte operativo.
    Explica, guía y acompaña procesos técnicos.
    """

    def __init__(self) -> None:
        prompt = load_text(PROMPTS_DIR / "support.md")
        contract = load_json(CONTRACTS_DIR / "support.json")

        super().__init__(
            name="support_agent",
            role="Soporte técnico y operativo",
            prompt=prompt,
            contract=contract,
        )

    def handle(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        context = context or {}

        # Por ahora, stub simple para validar estructura
        response_text = (
            "SupportAgent recibió la tarea correctamente. "
            "Aún estoy en modo stub, pero la estructura funciona."
        )

        return {
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context,
            "response": response_text,
            "contract": self.contract,
        }
