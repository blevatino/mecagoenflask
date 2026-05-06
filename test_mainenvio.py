import requests
import json

# Configuración
PUERTO_PRUEBA = 62262  # Puerto de mainenvioizquierda
URL = f"http://localhost:{PUERTO_PRUEBA}/"


def test_envio():
    # Test 1: Enviar JSON con estructura nueva
    print("=== Test 1: Enviar mensaje con estructura nueva ===")
    data = {"message": ["Hola mundo"], "counter": 5, "repetidores": ["Juan Perez"]}
    print(f"Enviando: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(URL, json=data, timeout=5)
        print(f"Respuesta: {response.status_code}")
        print(f"JSON: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

    print()

    # Test 2: Enviar JSON sin repetidores
    print("=== Test 2: Enviar mensaje sin repetidores ===")
    data = {"message": ["Test sin repetidores"], "counter": 0, "repetidores": []}
    print(f"Enviando: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(URL, json=data, timeout=5)
        print(f"Respuesta: {response.status_code}")
        print(f"JSON: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

    print()

    # Test 3: Enviar JSON vacío (solo counter)
    print("=== Test 3: Enviar JSON con counter alto ===")
    data = {
        "message": ["Mensaje límite"],
        "counter": 99,
        "repetidores": ["Otro usuario"],
    }
    print(f"Enviando: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(URL, json=data, timeout=5)
        print(f"Respuesta: {response.status_code}")
        print(f"JSON: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("Asegúrate de que mainenvioderecha.py esté corriendo en puerto 62262")
    print("Ejecuta: python mainenvioderecha.py")
    print()
    input("Presiona Enter para continuar con las pruebas...")
    test_envio()
