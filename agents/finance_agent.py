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


class FinanceAgent(BaseAgent):
    """
    Agente financiero: reportes, análisis, cálculos.
    """

    def __init__(self) -> None:
        prompt = load_text(PROMPTS_DIR / "finance.md")
        contract = load_json(CONTRACTS_DIR / "finance.json")

        super().__init__(
            name="finance_agent",
            role="Finanzas y análisis económico",
            prompt=prompt,
            contract=contract,
        )

    def handle(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}

        response_text = (
            "FinanceAgent recibió la tarea. Modo stub activo."
        )

        return {
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context,
            "response": response_text,
            "contract": self.contract,
        }
