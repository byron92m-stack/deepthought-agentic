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


class ToolsAgent(BaseAgent):
    """
    Agente especializado en decidir y coordinar herramientas.
    """

    def __init__(self) -> None:
        prompt = load_text(PROMPTS_DIR / "tools.md")
        contract = load_json(CONTRACTS_DIR / "tools.json")

        super().__init__(
            name="tools_agent",
            role="Coordinación de herramientas",
            prompt=prompt,
            contract=contract,
        )

    def handle(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}

        response_text = (
            "ToolsAgent recibió la tarea. Modo stub activo."
        )

        return {
            "agent": self.name,
            "role": self.role,
            "task": task,
            "context": context,
            "response": response_text,
            "contract": self.contract,
        }
