from flask import Flask, request, jsonify
import requests
import socket
import threading
import time

app = Flask(__name__)

# =============================================
#   CONFIGURÁ ESTA IP ANTES DE ARRANCAR
# =============================================
IP_SIGUIENTE = "192.168.220.130" #ip del de la izquierda

LIMITE_CONTADOR = 100

PuertoEnvio = 63028 # puerto propio
PuertoEscucha = 62262 # puerto del de la derecha

MI_NOMBRE = "Bruno Levatino"


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

    if MI_NOMBRE not in repetidores:
        repetidores.append(MI_NOMBRE)

    ip_local = get_ip_local()
    print(f"[{ip_local}] [{counter}] {message} - Repetidores: {repetidores}")

    if counter >= LIMITE_CONTADOR:
        print(f"[{ip_local}] Mensaje eliminado (limite {LIMITE_CONTADOR} alcanzado)")
        return jsonify({"status": "eliminado", "counter": counter}), 200

    def pasar_siguiente():
        try:
            url = f"http://{IP_SIGUIENTE}:{PuertoEnvio}/"
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
            print(f"Error al pasar a {IP_SIGUIENTE}: {str(e)}")

    threading.Thread(target=pasar_siguiente).start()

    return jsonify({"status": "ok", "counter": counter}), 200


def enviar_mensaje(mensaje):
    try:
        url = f"http://{IP_SIGUIENTE}:{PuertoEnvio}/"
        requests.post(
            url,
            json={"message": mensaje, "counter": 0, "repetidores": [MI_NOMBRE]},
            timeout=5,
        )
    except Exception as e:
        print(f"Error al enviar a {IP_SIGUIENTE}: {str(e)}")


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
    print(f"Servidor en {ip_local}:{PuertoEscucha} -> siguiente: {IP_SIGUIENTE}")

    threading.Thread(target=loop_input, daemon=True).start()

    app.run(host="0.0.0.0", port=PuertoEscucha, debug=False)
