import sys
import os
from datetime import datetime, timedelta, timezone

# Añadir el path de la app al sistema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.services.cliente_service import crear_cliente, listar_clientes

# CONFIGURACIÓN DE TEST LOCAL (SQLite)
TEST_DATABASE_URL = "sqlite:///./test_saas.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_saas_tests():
    print("[INFO] Iniciando Tests de Logica SaaS en SQLite Local...")
    Base.metadata.drop_all(bind=engine) # Limpiar rastro previo
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Crear un usuario DEMO (Límite 10 clientes)
        test_user = db.query(Usuario).filter(Usuario.email == "test_saas@cobrago.com").first()
        if not test_user:
            test_user = Usuario(
                username="saas_tester",
                email="test_saas@cobrago.com",
                hashed_password="fake",
                plan_suscripcion="demo",
                rol="cobrador",
                fecha_vencimiento=datetime.now(timezone.utc) + timedelta(days=30)
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)

        print(f"[OK] Usuario {test_user.username} (Plan: {test_user.plan_suscripcion}) listo.")

        # 2. Inyectar 10 clientes (Límite del plan Demo)
        print("[STEP] Inyectando 10 clientes (debe funcionar)...")
        for i in range(10):
            try:
                crear_cliente(db, f"Cliente {i}", f"1000{i}", test_user)
            except Exception as e:
                print(f"[ERROR] Error inesperado: {e}")

        # 3. Intentar inyectar el cliente 11 (Debe FALLAR)
        print("[TEST] Probando LIMITE DE PLAN (Cliente 11)...")
        try:
            crear_cliente(db, "Invasor", "100011", test_user)
            print("[FAIL] ERROR: El sistema permitio crear mas clientes de lo permitido en el plan Demo.")
        except ValueError as e:
            print(f"[SUCCESS] EXITO: El sistema bloqueo la creacion: {e}")

        # 4. Probar VENCIMIENTO
        print("[TEST] Probando VENCIMIENTO DE PLAN...")
        test_user.fecha_vencimiento = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()

        try:
            crear_cliente(db, "Vencido", "20000", test_user)
            print("[FAIL] ERROR: El sistema permitio crear datos con suscripcion vencida.")
        except ValueError as e:
            print(f"[SUCCESS] EXITO: El sistema bloqueo por vencimiento: {e}")

        # 5. Probar PRIVACIDAD (un cobrador no ve datos de otro)
        print("[TEST] Probando PRIVACIDAD DE COBRADORES...")
        other_user = Usuario(
            username="espia",
            email="espia@hack.com",
            hashed_password="fake",
            plan_suscripcion="demo",
            rol="cobrador"
        )
        db.add(other_user)
        db.commit()
        
        mis_clientes = listar_clientes(db, other_user)
        if len(mis_clientes) == 0:
            print(f"[SUCCESS] EXITO: El usuario '{other_user.username}' no ve los clientes del otro usuario.")
        else:
            print(f"[FAIL] ERROR: El usuario espia logro ver {len(mis_clientes)} clientes ajenos.")

    finally:
        # Limpieza (opcional)
        # db.query(Cliente).filter(Cliente.usuario_id == test_user.id).delete()
        # db.query(Usuario).filter(Usuario.id.in_([test_user.id, other_user.id])).delete()
        db.close()
        print("\n[FIN] Pruebas SaaS Finalizadas.")

if __name__ == "__main__":
    run_saas_tests()
