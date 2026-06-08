from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Cargamos la URL
connection_url = settings.DATABASE_URL

# Configuración condicional según el tipo de DB
if connection_url.startswith("sqlite"):
    # Parámetros para SQLite local
    engine = create_engine(
        connection_url, 
        connect_args={"check_same_thread": False}
    )
else:
    # Parámetros para Postgres (Render/Supabase)
    engine = create_engine(
        connection_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"sslmode": "require"}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
