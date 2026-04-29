from app.database import engine, SessionLocal
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("¡Conexión exitosa a Supabase!")
        print(f"Resultado: {result.fetchone()[0]}")
except Exception as e:
    print("Error al conectar a Supabase:")
    print(e)
