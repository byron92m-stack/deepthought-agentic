"""
Definición de contratos (schemas) para herramientas que deepthought puede usar.

Cada herramienta tiene:
- name: nombre que el LLM usará
- description: para qué sirve
- parameters: JSON schema de los argumentos
"""

TOOL_SCHEMAS = [
    # -----------------------------
    # FILES
    # -----------------------------
    {
        "name": "leer_archivo",
        "description": "Lee un archivo de texto y devuelve su contenido.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Ruta del archivo a leer."}
            },
            "required": ["path"],
        },
    },
    {
        "name": "escribir_archivo",
        "description": "Escribe contenido en un archivo de texto.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Ruta del archivo a escribir."},
                "contenido": {"type": "string", "description": "Contenido a escribir."},
            },
            "required": ["path", "contenido"],
        },
    },
    {
        "name": "listar_archivos",
        "description": "Lista archivos dentro de un directorio.",
        "parameters": {
            "type": "object",
            "properties": {
                "directorio": {"type": "string", "description": "Directorio a listar."}
            },
            "required": ["directorio"],
        },
    },

    # -----------------------------
    # FINANCE
    # -----------------------------
    {
        "name": "obtener_transacciones",
        "description": "Devuelve la lista completa de transacciones financieras.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "calcular_balance",
        "description": "Calcula ingresos, gastos y balance neto.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "clasificar_gastos",
        "description": "Agrupa gastos por categoría.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },

    # -----------------------------
    # ADMIN
    # -----------------------------
    {
        "name": "crear_tarea",
        "description": "Crea una nueva tarea administrativa.",
        "parameters": {
            "type": "object",
            "properties": {
                "descripcion": {"type": "string", "description": "Descripción de la tarea."}
            },
            "required": ["descripcion"],
        },
    },
    {
        "name": "listar_tareas",
        "description": "Lista todas las tareas registradas.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "actualizar_tarea",
        "description": "Actualiza el estado de una tarea.",
        "parameters": {
            "type": "object",
            "properties": {
                "id_tarea": {"type": "string", "description": "ID de la tarea."},
                "estado": {"type": "string", "description": "Nuevo estado."},
            },
            "required": ["id_tarea", "estado"],
        },
    },
]
