import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import *
from app.services.pago_service import registrar_pago
from app.schemas.pago import PagoResponse
import traceback
from decimal import Decimal

def debug_pago():
    db = SessionLocal()
    print("--- DEBUGGING REGISTRAR_PAGO ---")
    
    prestamo = db.query(Prestamo).first()
    if not prestamo:
        print("Error: No hay préstamos para probar.")
        return

    usuario = db.query(Usuario).first()
    user_id = usuario.id if usuario else 1

    try:
        print(f"Probando pago para Prestamo ID: {prestamo.id}, Usuario={user_id}")
        res = registrar_pago(db, prestamo_id=prestamo.id, monto=Decimal('10.00'), usuario_id=user_id, comentario="Prueba 2")
        print(f"EXITO DB: {res}")
        # Test serialization
        res_schema = PagoResponse.model_validate(res)
        print(f"EXITO SCHEMA: {res_schema}")
    except Exception:
        print("\n--- ¡ERROR DE EJECUCIÓN DETECTADO! ---")
        traceback.print_exc()

if __name__ == "__main__":
    debug_pago()
