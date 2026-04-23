from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine, Base
from app.models import * # Carga centralizada de todos los modelos
from app.routes import clientes, prestamo as prestamo_router, pagos
from app.routes import auth

# Crear tablas en la DB (en producción usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CobraGo API", version="1.0.0")

@app.on_event("startup")
def startup_db_check():
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

# Incluir routers
app.include_router(clientes.router)
app.include_router(prestamo_router.router)
app.include_router(pagos.router)

# Auth
app.include_router(auth.router)

# Stats
from app.routes import stats
app.include_router(stats.router)