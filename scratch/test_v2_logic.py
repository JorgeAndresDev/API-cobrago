import requests
import json
import uuid

BASE_URL = "https://api-cobrago.onrender.com" # URL de Produccion detectada en axios.ts

def test_full_workflow():
    print("--- INICIANDO PRUEBA INTEGRAL DE API COBRAGO V2 ---\n")
    
    # 1. Login
    print("[1] Probando Login...")
    login_data = {
        "correo": "admin@cobrago.com",
        "password": "adminpassword"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"X Error en login: {response.status_code} - {response.text}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("> Login exitoso.\n")
    except Exception as e:
        print(f"X Error de conexion: {e}")
        return

    # 2. Crear Cliente
    print("[2] Creando Cliente de prueba...")
    cedula_test = f"1010{uuid.uuid4().hex[:4]}"
    cliente_data = {
        "nombre": "Juan Prueba V2",
        "cedula": cedula_test,
        "telefono": "3001234567",
        "direccion": "Calle Falsa 123",
        "nivel_riesgo": "Bajo"
    }
    res_cliente = requests.post(f"{BASE_URL}/clientes/", json=cliente_data, headers=headers)
    if res_cliente.status_code in [200, 201]:
        cliente = res_cliente.json()
        cliente_id = cliente["id"]
        print(f"> Cliente OK: {cliente['nombre']} (ID: {cliente_id})")
    else:
        print(f"X Error cliente: {res_cliente.text}")
        return

    # 3. Crear Préstamo con Intereses y UUID 
    print("\n[3] Creando Prestamo con Intereses y Sincronizacion (V2)...")
    loan_uuid = str(uuid.uuid4())
    monto_base = 100000
    porcentaje = 20
    monto_total = monto_base + (monto_base * porcentaje / 100)
    
    prestamo_data = {
        "uuid": loan_uuid,
        "monto": monto_base,
        "monto_total": monto_total,
        "tipo_interes": "mensual",
        "porcentaje_interes": porcentaje,
        "num_cuotas": 4,
        "frecuencia_pago": "semanal",
        "cliente_id": cliente_id
    }
    
    res_prestamo = requests.post(f"{BASE_URL}/prestamos/", json=prestamo_data, headers=headers)
    if res_prestamo.status_code in [200, 201]:
        loan = res_prestamo.json()
        print(f"> Prestamo OK.")
        print(f"  - UUID: {loan_uuid}")
        print(f"  - Monto Total: {loan['monto_total']}")
        
        # Verificar cuotas
        cuotas = loan.get("cuotas", [])
        if cuotas:
            print(f"  - Cuotas generadas: {len(cuotas)}")
            monto_cuota = float(cuotas[0]['monto_cuota'])
            esperado = monto_total / 4
            if abs(monto_cuota - esperado) < 0.1:
                print("  - RESULTADO: CALCULO DE INTERESES CORRECTO.")
            else:
                print(f"  - Error en calculo: esperado {esperado}, llego {monto_cuota}")
    else:
        print(f"X Error prestamo: {res_prestamo.text}")

    # 4. Probar Cambio de Contraseña
    print("\n[4] Probando Cambio de Contrasena...")
    pass_data = {
        "current_password": "adminpassword",
        "new_password": "newpassword123"
    }
    res_pass = requests.post(f"{BASE_URL}/auth/change-password", json=pass_data, headers=headers)
    if res_pass.status_code == 200:
        print("> Contrasena cambiada exitosamente.")
        
        # Revertir
        requests.post(f"{BASE_URL}/auth/change-password", 
                      json={"current_password": "newpassword123", "new_password": "adminpassword"}, 
                      headers=headers)
        print("> Contrasena restablecida.")
    else:
        print(f"X Error cambio pass: {res_pass.text}")

    print("\n--- PRUEBA FINALIZADA CON EXITO ---")

if __name__ == "__main__":
    test_full_workflow()
