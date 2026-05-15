
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
sudo snap install astral-uv --classic

```bash
# Crear entorno virtual
uv venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
uv pip install -r requirements.txt
```
## Ejecutar el servidor
python mainenvioizquieda.py
python mainenvioderecha.py

sudo docker build -t nodo-flask .

## Derecha
sudo docker run --rm -it --network=host \
-e NOMBRE_NODO="Bruno Levatino" \
-e IP_SIGUIENTE="192.168.220.107" \
-e PUERTO_ENVIO=63028 \
-e PUERTO_ESCUCHA=49181 \
-e LIMITE_CONTADOR=6 \
nodo-flask

## Izquierda
sudo docker run --rm -it --network=host \
-e NOMBRE_NODO="Bruno Levatino" \
-e IP_SIGUIENTE="192.168.220.130" \
-e PUERTO_ENVIO=63028 \
-e PUERTO_ESCUCHA=62262 \
-e LIMITE_CONTADOR=6 \
nodo-flask





