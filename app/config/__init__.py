import os
from dotenv import load_dotenv

# Cargar variables desde .env si existe (útil para desarrollo local)
load_dotenv()

class Settings:
    # Base de Datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/cobrago")
    
    # Seguridad
    SECRET_KEY: str = os.getenv("SECRET_KEY", "jorgeandresg1207")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

settings = Settings()
