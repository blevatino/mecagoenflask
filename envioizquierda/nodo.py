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

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_RED = "\033[41m"


def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def print_box(content, color=CYAN):
    width = 70
    print(f"{color}{BOLD}╔{'═' * (width - 2)}╗{RESET}")
    for line in content.split("\n"):
        padding = width - len(line) - 4
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(
            f"{color}{BOLD}║{RESET}{' ' * left_pad}{line}{' ' * right_pad}{color}{BOLD}║{RESET}"
        )
    print(f"{color}{BOLD}╚{'═' * (width - 2)}╝{RESET}")


def print_separator(color=DIM):
    print(f"{color}{'─' * 70}{RESET}")


@app.route("/", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()
    message = data.get("name", [])
    counter = data.get("counter", 0) + 1
    repetidores = data.get("repetidores", [])

    repetidores.append(NOMBRE_NODO)

    ip_local = get_ip_local()

    print()
    print_separator(GREEN)
    print(f"{GREEN}{BOLD}📩 MENSAJE RECIBIDO{RESET}")
    print_separator(DIM)
    print(f"   {CYAN}📍 De:{RESET}       {ip_local}:{PUERTO_ESCUCHA}")
    print(f"   {YELLOW}🔢 Contador:{RESET} {BOLD}{counter}{RESET} / {LIMITE_CONTADOR}")
    print_separator(DIM)
    print(f"   {MAGENTA}👤 Nombre:{RESET}")
    print(f"      {WHITE}{message}{RESET}")
    print_separator(DIM)
    print(f"   {BLUE}🔄 Recorrido:{RESET}")
    for i, nodo in enumerate(repetidores):
        es_ultima_aparicion = nodo == NOMBRE_NODO and i == len(repetidores) - 1
        marca = f"{GREEN}✓{RESET}" if es_ultima_aparicion else " "
        flecha = "→" if i < len(repetidores) - 1 else " "
        print(f"      {marca} [{i + 1}] {nodo} {flecha}")
    print_separator(DIM)

    if counter >= LIMITE_CONTADOR:
        print(f"\n{RED}{BOLD}💀 MENSAJE ELIMINADO{RESET}")
        print(f"{RED}   Límite de {LIMITE_CONTADOR} reenvíos alcanzado{RESET}")
        print_separator(RED)
        return jsonify({"status": "eliminado", "counter": counter}), 200

    destino = f"{IP_SIGUIENTE}:{PUERTO_ENVIO}"
    print(f"{GREEN}➡️  Reenviando a: {BOLD}{destino}{RESET}")
    print_separator(GREEN)

    def pasar_siguiente():
        try:
            url = f"http://{IP_SIGUIENTE}:{PUERTO_ENVIO}/"
            requests.post(
                url,
                json={
                    "name": message,
                    "counter": counter,
                    "repetidores": repetidores,
                },
                timeout=5,
            )
        except Exception as e:
            print(f"\n{RED}❌ Error al enviar a {destino}:{RESET}")
            print(f"   {e}")
            print_separator(RED)

    threading.Thread(target=pasar_siguiente).start()

    return jsonify({"status": "ok", "counter": counter}), 200


def enviar_mensaje(mensaje):
    try:
        destino = f"{IP_SIGUIENTE}:{PUERTO_ENVIO}"
        print()
        print_separator(YELLOW)
        print(f"{YELLOW}{BOLD}🚀 ENVIANDO NUEVO MENSAJE{RESET}")
        print_separator(DIM)
        print(f"   {CYAN}📤 Destino:{RESET}  {destino}")
        print(f"   {BLUE}👤 Remitente:{RESET} {NOMBRE_NODO}")
        print(f"   {MAGENTA}👤 Nombre:{RESET}")
        print(f"      {WHITE}{mensaje}{RESET}")
        print_separator(YELLOW)

        url = f"http://{IP_SIGUIENTE}:{PUERTO_ENVIO}/"
        requests.post(
            url,
            json={"name": mensaje, "counter": 0, "repetidores": [NOMBRE_NODO]},
            timeout=5,
        )
    except Exception as e:
        print(f"\n{RED}❌ Error al enviar:{RESET}")
        print(f"   {e}")
        print_separator(RED)


def loop_input():
    time.sleep(1)
    print()
    print_separator(CYAN)
    print(f"{CYAN}{BOLD}✏️  ESCRIBE UN NOMBRE Y PRESIONA ENTER{RESET}")
    print_separator(DIM)
    while True:
        try:
            mensaje = input(f"{GREEN}>{RESET} ")
            if mensaje.strip():
                threading.Thread(target=enviar_mensaje, args=(mensaje.strip(),)).start()
        except EOFError:
            break


if __name__ == "__main__":
    ip_local = get_ip_local()

    print()
    print_box(f"{BOLD}🚀  {NOMBRE_NODO.upper()}  🚀{RESET}", GREEN)
    print()
    print(f"   {CYAN}📍 IP Local:{RESET}     {ip_local}")
    print(f"   {BLUE}👂 Escuchando:{RESET}  {ip_local}:{PUERTO_ESCUCHA}")
    print(f"   {GREEN}➡️  Destino:{RESET}     {IP_SIGUIENTE}:{PUERTO_ENVIO}")
    print(f"   {YELLOW}🔢 Límite:{RESET}      {LIMITE_CONTADOR} reenvíos")
    print()
    print_separator()

    threading.Thread(target=loop_input, daemon=True).start()

    app.run(host="0.0.0.0", port=PUERTO_ESCUCHA, debug=False)
