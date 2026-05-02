from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base
from app.models import * # Carga centralizada de todos los modelos
from app.routes import clientes, prestamo as prestamo_router, pagos
from app.routes import auth

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
    print("INFO:     Iniciando conexión a la base de datos...")
    try:
        # Crear tablas en la DB
        Base.metadata.create_all(bind=engine)
        print("INFO:     Conexión exitosa y tablas verificadas.")
        
        # Auto-parche para asegurar columnas y tablas nuevas sin migraciones manuales
        with engine.connect() as conn:
            try:
                # 1. Tabla Clientes
                conn.execute(text("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS usuario_id INTEGER;"))
                
                # 2. Tabla Prestamos (Nuevas columnas y limpieza de antiguas)
                conn.execute(text("ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS monto NUMERIC(12, 2);"))
                conn.execute(text("ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS num_cuotas INTEGER;"))
                conn.execute(text("ALTER TABLE prestamos ADD COLUMN IF NOT EXISTS estado VARCHAR DEFAULT 'pendiente';"))
                
                # 3. Tabla Cuotas
                conn.execute(text("ALTER TABLE cuotas ADD COLUMN IF NOT EXISTS monto_esperado NUMERIC(12, 2);"))
                
                # 4. Tabla de Auditoría (HistoriaOperacion)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS historial_operaciones (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
                        accion VARCHAR NOT NULL,
                        monto NUMERIC(12, 2),
                        entidad_id INTEGER,
                        detalles VARCHAR,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                conn.commit()
                print("INFO:     Database schema COMPATIBILITY SYNC completed.")
            except Exception as e:
                print(f"INFO:     Schema sync notice: {e}")
                conn.rollback()
    except Exception as e:
        print(f"ERROR FATAL DE BASE DE DATOS: {e}")
        # No matamos la app para que Render pueda registrar el log y la ponga Live

# Incluir routers
app.include_router(clientes.router)
app.include_router(prestamo_router.router)
app.include_router(pagos.router)

# Auth
app.include_router(auth.router)

# Stats
from app.routes import stats
app.include_router(stats.router)