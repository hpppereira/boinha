import websocket
import json
import csv
import time
from collections import deque
import threading
import pandas as pd
from datetime import timedelta

# --- Configurações ---
csv_filename = "data/sensores.csv"
MAX_LINES = 5000       # número máximo de linhas no CSV
SAVE_INTERVAL = 1.0    # salva no CSV a cada X segundos
SENSOR_TYPES = [
    "accelerometer",
    "gyroscope",
    "linear_acceleration",
    "orientation"
]

ip = "192.168.0.20"
port = "8080"
RETRY_DELAY = 5        # segundos para esperar antes de reconectar

# --- Buffer em memória ---
buffer = deque(maxlen=MAX_LINES)
buffer_lock = threading.Lock()

# --- Inicializa CSV se não existir ---
try:
    with open(csv_filename, "r") as f:
        pass
except FileNotFoundError:
    with open(csv_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["datetime", "wall_time", "sensor_type", "timestamp_ns", "accuracy", "x", "y", "z"])

# --- Função para salvar buffer no CSV ---
def save_buffer_to_csv():
    while True:
        time.sleep(SAVE_INTERVAL)
        with buffer_lock:
            if buffer:
                with open(csv_filename, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["datetime", "wall_time", "sensor_type", "timestamp_ns", "accuracy", "x", "y", "z"])
                    writer.writerows(buffer)
                print(f"Salvo {len(buffer)} linhas no CSV")

# --- WebSocket callbacks ---
def on_message(ws, message):
    d = json.loads(message)
    sensor_type = d.get("type")
    values = d.get("values", [None, None, None])
    accuracy = d.get("accuracy")
    timestamp_ns = d.get("timestamp")
    wall_time = time.time()
    datetime = pd.to_datetime(wall_time, unit='s') - timedelta(hours=3)

    row = [datetime, wall_time, sensor_type, timestamp_ns, accuracy, values[0], values[1], values[2]]

    with buffer_lock:
        buffer.append(row)

    print(f"{sensor_type}: {values}")

def on_error(ws, error):
    print("error occurred:", error)

def on_close(ws, close_code, reason):
    print("connection closed:", reason)

def on_open(ws):
    print("connected")

# --- Função de conexão com reconexão automática ---
def connect_with_retry(url):
    while True:
        try:
            ws = websocket.WebSocketApp(
                url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            # ping_interval mantém conexão viva
            ws.run_forever(ping_interval=30, ping_timeout=10)
        except Exception as e:
            print("Erro na conexão:", e)

        print(f"Tentando reconectar em {RETRY_DELAY} segundos...")
        time.sleep(RETRY_DELAY)

# --- Monta URL para múltiplos sensores ---
types_str = ",".join([f'"android.sensor.{t}"' for t in SENSOR_TYPES])
url = f'ws://{ip}:{port}/sensors/connect?types=[{types_str}]'

# --- Inicia thread para salvar buffer ---
save_thread = threading.Thread(target=save_buffer_to_csv, daemon=True)
save_thread.start()

# --- Conecta com retry ---
connect_with_retry(url)
