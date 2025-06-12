"""
Constantes del sistema de inventario de laboratorio
"""

# Bodegas fijas del sistema (no se pueden modificar por UI)
FIXED_WAREHOUSES = [
    {
        "code": "W01",
        "name": "Bodega Principal W01",
        "description": "Bodega principal para almacenamiento de muestras procesadas",
        "capacity": 1000.0
    },
    {
        "code": "W02", 
        "name": "Bodega Secundaria W02",
        "description": "Bodega secundaria para muestras en proceso",
        "capacity": 750.0
    },
    {
        "code": "W03",
        "name": "Bodega Almacén W03", 
        "description": "Bodega de almacén para muestras de archivo",
        "capacity": 500.0
    },
    {
        "code": "W04",
        "name": "Bodega Temporal W04",
        "description": "Bodega temporal para muestras en tránsito",
        "capacity": 500.0
    },
        {
        "code": "VAS",
        "name": "Bodega VAS",
        "description": "Bodega principal",
        "capacity": 300.0
    }
]

# Tipos de acciones para auditoría
AUDIT_ACTIONS = {
    "CREATE": "Creación",
    "UPDATE": "Actualización", 
    "DELETE": "Eliminación lógica",
    "MOVE": "Movimiento entre bodegas",
    "RESTORE": "Restauración"
}

# Estados de registros
RECORD_STATUS = {
    "ACTIVE": True,
    "INACTIVE": False
}

# Unidades de medida predefinidas
MEASUREMENT_UNITS = [
    "kg",    # kilogramos
    "g",     # gramos
    "mg",    # miligramos
    "t",     # toneladas
    "L",     # litros
    "mL",    # mililitros
    "m³",    # metros cúbicos
    "pcs",   # piezas
    "box",   # cajas
]

# Tipos de calidad predefinidos
QUALITY_TYPES = [
    "Alta",
    "Media", 
    "Baja",
    "Premium",
    "Estándar",
    "Defectuosa",
    "En revisión"
]

# Tipos de mina predefinidos
MINE_TYPES = [
    "Cielo abierto",
    "Subterránea",
    "Placer",
    "Cantera",
    "Pozo",
    "Otra"
]

# Códigos de respuesta de la API
API_RESPONSES = {
    "SUCCESS": {"code": 200, "message": "Operación exitosa"},
    "CREATED": {"code": 201, "message": "Recurso creado exitosamente"}, 
    "BAD_REQUEST": {"code": 400, "message": "Solicitud incorrecta"},
    "NOT_FOUND": {"code": 404, "message": "Recurso no encontrado"},
    "CONFLICT": {"code": 409, "message": "Conflicto con recurso existente"},
    "SERVER_ERROR": {"code": 500, "message": "Error interno del servidor"}
}

# Configuración de validaciones
VALIDATION_RULES = {
    "sample_number": {
        "min_length": 3,
        "max_length": 50,
        "pattern": r"^[A-Z0-9\-_]+$"  # Solo mayúsculas, números, guiones y guiones bajos
    },
    "client_name": {
        "min_length": 2,
        "max_length": 100
    },
    "mine_name": {
        "min_length": 2, 
        "max_length": 100
    },
    "batch_number": {
        "min_length": 3,
        "max_length": 50,
        "pattern": r"^[A-Z0-9\-_]+$"
    },
    "quantity": {
        "min_value": 0.0,
        "max_value": 999999.99
    },
    "weight": {
        "min_value": 0.0,
        "max_value": 999999.99
    }
}

# Mensajes de error
ERROR_MESSAGES = {
    "REQUIRED_FIELD": "Este campo es requerido",
    "INVALID_FORMAT": "Formato inválido",
    "DUPLICATE_ENTRY": "Ya existe un registro con este valor",
    "INVALID_REFERENCE": "Referencia inválida",
    "INSUFFICIENT_QUANTITY": "Cantidad insuficiente",
    "WAREHOUSE_CAPACITY_EXCEEDED": "Capacidad de bodega excedida",
    "INVALID_DATE": "Fecha inválida",
    "PERMISSION_DENIED": "Permisos insuficientes"
}