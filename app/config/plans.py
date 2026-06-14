# Configuración de Planes SaaS CobraGo

PLANS = {
    "demo": {
        "max_cobradores": 1,
        "max_clientes": 10,
        "funciones": ["basico"],
        "nombre": "Plan Demo"
    },
    "basico": {
        "max_cobradores": 1,
        "max_clientes": 500,
        "funciones": ["basico", "reportes", "exportar"],
        "nombre": "Plan Básico"
    },
    "profesional": {
        "max_cobradores": 5,
        "max_clientes": 5000,
        "funciones": ["basico", "reportes", "exportar", "estadisticas_avanzadas"],
        "nombre": "Plan Profesional"
    },
    "empresa": {
        "max_cobradores": 9999,
        "max_clientes": 999999,
        "funciones": ["basico", "reportes", "exportar", "estadisticas_avanzadas", "multiusuario"],
        "nombre": "Plan Empresa"
    }
}

def get_plan_config(plan_name: str):
    return PLANS.get(plan_name.lower(), PLANS["demo"])
