import os
import json
import uuid
from typing import List, Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TASKS_PATH = os.path.join(BASE_DIR, "data", "tareas.json")

def _leer_tareas() -> List[Dict[str, Any]]:
    if not os.path.exists(TASKS_PATH):
        return []
    with open(TASKS_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _guardar_tareas(tareas: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(TASKS_PATH), exist_ok=True)
    with open(TASKS_PATH, "w", encoding="utf-8") as f:
        json.dump(tareas, f, indent=2, ensure_ascii=False)

def crear_tarea(descripcion: str) -> dict:
    tareas = _leer_tareas()
    tarea = {
        "id": str(uuid.uuid4()),
        "descripcion": descripcion,
        "estado": "pendiente",
    }
    tareas.append(tarea)
    _guardar_tareas(tareas)
    return tarea

def listar_tareas() -> list:
    return _leer_tareas()

def actualizar_tarea(id_tarea: str, estado: str) -> str:
    tareas = _leer_tareas()
    for t in tareas:
        if t.get("id") == id_tarea:
            t["estado"] = estado
    _guardar_tareas(tareas)
    return "ok"
