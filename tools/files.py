import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def _safe_path(path: str) -> str:
    full_path = os.path.abspath(os.path.join(BASE_DIR, path))
    if not full_path.startswith(BASE_DIR):
        raise ValueError("Ruta fuera del directorio permitido")
    return full_path

def leer_archivo(path: str) -> str:
    full_path = _safe_path(path)
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()

def escribir_archivo(path: str, contenido: str) -> str:
    full_path = _safe_path(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(contenido)
    return "ok"

def listar_archivos(directorio: str) -> list:
    full_dir = _safe_path(directorio)
    if not os.path.isdir(full_dir):
        return []
    return os.listdir(full_dir)
