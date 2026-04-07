import os
import json
from typing import List, Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRANSACCIONES_PATH = os.path.join(BASE_DIR, "data", "transacciones.json")

def _leer_transacciones() -> List[Dict[str, Any]]:
    if not os.path.exists(TRANSACCIONES_PATH):
        return []
    with open(TRANSACCIONES_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def obtener_transacciones() -> list:
    return _leer_transacciones()

def calcular_balance() -> dict:
    data = _leer_transacciones()
    ingresos = sum(t.get("monto", 0) for t in data if t.get("tipo") == "ingreso")
    gastos = sum(t.get("monto", 0) for t in data if t.get("tipo") == "gasto")
    return {
        "ingresos": ingresos,
        "gastos": gastos,
        "balance": ingresos - gastos,
    }

def clasificar_gastos() -> dict:
    data = _leer_transacciones()
    categorias = {}
    for t in data:
        if t.get("tipo") == "gasto":
            cat = t.get("categoria", "sin_categoria")
            categorias.setdefault(cat, 0)
            categorias[cat] += t.get("monto", 0)
    return categorias
