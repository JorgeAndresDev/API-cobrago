from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app.models import * # Carga centralizada de todos los modelos
from app.routes import clientes, prestamo as prestamo_router, pagos
from app.routes import auth, admin

app = FastAPI(title="CobraGo API", version="1.0.0")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, especificar los dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db_check():
    print("INFO:     Verificando BD...")
    try:
        Base.metadata.create_all(bind=engine)
        # Parcheo manual silencioso
        with engine.connect() as conn:
            # Lista de comandos para ejecutar uno a uno de forma segura
            commands = [
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS usuario_id INTEGER;",
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS latitud FLOAT;",
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS longitud FLOAT;",
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS observaciones TEXT;",
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS nivel_riesgo VARCHAR DEFAULT 'Bajo';",
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS foto_url VARCHAR;",
                "ALTER TABLE clientes ADD COLUMN IF NOT EXISTS foto_local_path VARCHAR;",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS uuid VARCHAR;",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS monto_total NUMERIC(12, 2);",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS tipo_interes VARCHAR;",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS porcentaje_interes FLOAT;",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS monto NUMERIC(12, 2);",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS num_cuotas INTEGER;",
                "ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS estado VARCHAR DEFAULT 'pendiente';",
                "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rol VARCHAR DEFAULT 'cobrador';",
                "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS estado_cuenta VARCHAR DEFAULT 'activo';",
                "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS plan_suscripcion VARCHAR DEFAULT 'basico';",
                "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS fecha_vencimiento TIMESTAMP;"
            ]
            for cmd in commands:
                try:
                    conn.execute(text(cmd))
                    conn.commit()
                except:
                    conn.rollback() # Ignoramos si la columna ya existe o falla el comando individual
        print("INFO:     BD lista.")
    except Exception as e:
        print(f"ALERTA: Error en startup: {e}")
# Incluir routers
app.include_router(clientes.router)
app.include_router(prestamo_router.router)
app.include_router(pagos.router)

# Auth
app.include_router(auth.router)
app.include_router(admin.router)

# Stats
from app.routes import stats
app.include_router(stats.router)