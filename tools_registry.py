"""
Registro central de herramientas para deepthought.

Este módulo expone un diccionario TOOLS_REGISTRY
que mapea nombres de herramienta a funciones Python reales.
"""

from typing import Any, Callable, Dict

from tools import files, finance, admin


# Tipo genérico para una herramienta
ToolFunc = Callable[..., Any]


TOOLS_REGISTRY: Dict[str, ToolFunc] = {
    # Files
    "leer_archivo": files.leer_archivo,
    "escribir_archivo": files.escribir_archivo,
    "listar_archivos": files.listar_archivos,

    # Finance
    "obtener_transacciones": finance.obtener_transacciones,
    "calcular_balance": finance.calcular_balance,
    "clasificar_gastos": finance.clasificar_gastos,

    # Admin
    "crear_tarea": admin.crear_tarea,
    "listar_tareas": admin.listar_tareas,
    "actualizar_tarea": admin.actualizar_tarea,
}


def ejecutar_herramienta(nombre: str, *args, **kwargs) -> Any:
    """
    Ejecuta una herramienta por nombre.
    Lanza KeyError si la herramienta no existe.
    """
    if nombre not in TOOLS_REGISTRY:
        raise KeyError(f"Herramienta no registrada: {nombre}")
    func = TOOLS_REGISTRY[nombre]
    return func(*args, **kwargs)
