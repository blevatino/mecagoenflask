import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import requests
import socket
import threading
import time

load_dotenv()

app = Flask(__name__)

NOMBRE_NODO = os.getenv("NOMBRE_NODO", "Nodo-Sin-Nombre")
IP_SIGUIENTE = os.getenv("IP_SIGUIENTE", "127.0.0.1")
PUERTO_ENVIO = int(os.getenv("PUERTO_ENVIO", "5000"))
PUERTO_ESCUCHA = int(os.getenv("PUERTO_ESCUCHA", "5000"))
LIMITE_CONTADOR = int(os.getenv("LIMITE_CONTADOR", "100"))


def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


@app.route("/", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()
    message = data.get("message", [])
    counter = data.get("counter", 0) + 1
    repetidores = data.get("repetidores", [])

    if NOMBRE_NODO not in repetidores:
        repetidores.append(NOMBRE_NODO)

    ip_local = get_ip_local()
    print(
        f"[{ip_local}:{PUERTO_ESCUCHA}] [{counter}] {message} - Repetidores: {repetidores}"
    )

    if counter >= LIMITE_CONTADOR:
        print(f"[{ip_local}] Mensaje eliminado (limite {LIMITE_CONTADOR} alcanzado)")
        return jsonify({"status": "eliminado", "counter": counter}), 200

    def pasar_siguiente():
        try:
            url = f"http://{IP_SIGUIENTE}:{PUERTO_ENVIO}/"
            requests.post(
                url,
                json={
                    "message": message,
                    "counter": counter,
                    "repetidores": repetidores,
                },
                timeout=5,
            )
        except Exception as e:
            print(f"Error al pasar a {IP_SIGUIENTE}:{PUERTO_ENVIO}: {str(e)}")

    threading.Thread(target=pasar_siguiente).start()

    return jsonify({"status": "ok", "counter": counter}), 200


def enviar_mensaje(mensaje):
    try:
        url = f"http://{IP_SIGUIENTE}:{PUERTO_ENVIO}/"
        requests.post(
            url,
            json={"message": mensaje, "counter": 0, "repetidores": [NOMBRE_NODO]},
            timeout=5,
        )
    except Exception as e:
        print(f"Error al enviar a {IP_SIGUIENTE}:{PUERTO_ENVIO}: {str(e)}")


def loop_input():
    time.sleep(1)
    while True:
        try:
            mensaje = input()
            if mensaje.strip():
                threading.Thread(target=enviar_mensaje, args=(mensaje.strip(),)).start()
        except EOFError:
            break


if __name__ == "__main__":
    ip_local = get_ip_local()
    print(f"=== {NOMBRE_NODO} ===")
    print(f"Escuchando en: {ip_local}:{PUERTO_ESCUCHA}")
    print(f"Enviando a:    {IP_SIGUIENTE}:{PUERTO_ENVIO}")
    print(f"Límite contador: {LIMITE_CONTADOR}")
    print("=" * 50)

    threading.Thread(target=loop_input, daemon=True).start()

    app.run(host="0.0.0.0", port=PUERTO_ESCUCHA, debug=False)
