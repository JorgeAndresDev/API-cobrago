import sys
import os
sys.path.append(os.getcwd())

from app.database import SessionLocal
# Centralized import
from app.models import *
from app.services.prestamo_service import crear_prestamo
from app.schemas.prestamo import PrestamoCreate
import traceback

def debug_loan_v2():
    db = SessionLocal()
    print("--- DEBUGGING CREAR_PRESTAMO (V2) ---")
    
    cliente = db.query(Cliente).first()
    if not cliente:
        print("Error: No hay clientes.")
        return

    data = PrestamoCreate(
        cliente_id=cliente.id, 
        monto=500.00, 
        frecuencia_pago='semanal', 
        num_cuotas=4
    )
    
    try:
        # Usamos el ID del primer usuario que encontremos
        user = db.query(Usuario).first()
        user_id = user.id if user else 1
        
        print(f"Probando: Cliente={cliente.id}, Usuario={user_id}")
        res = crear_prestamo(db, data, usuario_id=user_id)
        print(f"EXITO: {res}")
    except Exception:
        print("\n--- ¡ERROR DE EJECUCIÓN DETECTADO! ---")
        traceback.print_exc()

if __name__ == "__main__":
    debug_loan_v2()
