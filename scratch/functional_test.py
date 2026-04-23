import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("\n--- INICIANDO TEST DE FLUJO API ---")
    ts = int(time.time())
    unique_user = f"tester_{ts}"
    user_data = {
        "username": unique_user,
        "email": f"{unique_user}@test.com",
        "password": "password123"
    }

    try:
        # 1. Registro
        print(f"1. Registrando: {unique_user}...")
        reg_res = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if reg_res.status_code != 201:
            print(f"ERROR Registro: {reg_res.text}")
            return
        print("PASS: Usuario registrado.")

        # 2. Login
        print("2. Obteniendo Token...")
        login_payload = {"correo": user_data["email"], "password": user_data["password"]}
        log_res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        if log_res.status_code != 200:
            print(f"ERROR Login: {log_res.text}")
            return
        
        token = log_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("PASS: Login exitoso.")

        # 4. Refrescar Token
        print("4. Probando Refresh Token...")
        refresh_token = log_res.json()["refresh_token"]
        ref_res = requests.post(f"{BASE_URL}/auth/refresh?refresh_token={refresh_token}")
        if ref_res.status_code != 200:
            print(f"ERROR Refresh: {ref_res.text}")
            return
        
        new_token = ref_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {new_token}"}
        print("PASS: Refresh Token exitoso.")

        # 5. Crear Cliente
        print("5. Creando Cliente con nuevo Token...")
        client_data = {
            "nombre": f"Cliente Certificado {ts}",
            "cedula": f"CC-{ts}",
            "telefono": "555-TEST",
            "direccion": "Laboratorio de Pruebas"
        }
        clie_res = requests.post(f"{BASE_URL}/clientes/", json=client_data, headers=headers)
        if clie_res.status_code != 200:
            print(f"ERROR Cliente: {clie_res.text}")
            return
        
        cliente_id = clie_res.json()["id"]
        print(f"PASS: Cliente creado con ID: {cliente_id}")

        # 6. Crear Préstamo y Auditoría
        print("6. Generando Préstamo y Auditoría...")
        loan_data = {
            "monto": 1000,
            "frecuencia_pago": "mensual",
            "num_cuotas": 12
        }
        loan_res = requests.post(f"{BASE_URL}/clientes/{cliente_id}/prestamos", json=loan_data, headers=headers)
        if loan_res.status_code != 200:
            print(f"ERROR Préstamo: {loan_res.text}")
            return
        
        print("\nRESULTADO: FLUJO COMPLETO VERIFICADO EXITOSAMENTE!")
        print(f"Prestamo #{loan_res.json()['id']} activo.")

    except requests.exceptions.ConnectionError:
        print(f"\nERROR: La API no responde.")

if __name__ == "__main__":
    run_test()
