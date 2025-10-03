import websocket
import json
import csv
import time

# Nome do arquivo CSV
csv_filename = "data/sensores.csv"

# cria e escreve cabeçalho no CSV
with open(csv_filename, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["wall_time", "sensor_type", "timestamp_ns", "accuracy", "x", "y", "z"])

def on_message(ws, message):
    d = json.loads(message)

    sensor_type = d.get("type")
    values = d.get("values", [None, None, None])
    accuracy = d.get("accuracy")
    timestamp_ns = d.get("timestamp")   # timestamp do Android (ns desde boot)
    wall_time = time.time()             # tempo Unix "real" no PC

    row = [wall_time, sensor_type, timestamp_ns, accuracy] + values

    # salva no CSV
    with open(csv_filename, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    # print("Salvo:", row)
    print(d)


def on_error(ws, error):
    print("error occurred ", error)

def on_close(ws, close_code, reason):
    print("connection closed : ", reason)

def on_open(ws):
    print("connected")

def connect(url):
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()

# configuração
ip = "192.168.0.20"
port = "8080"

type1 = "accelerometer"
type2 = "gyroscope"
type3 = "magnetic_field"
type4 = "tilt_detector"
type5 = "device_orientation"
type6 = "linear_acceleration"
type7 = "rotation_vector"
type8 = "orientation"

# conecta pedindo múltiplos sensores
url = (
    f'ws://{ip}:{port}/sensors/connect?types=['
    f'"android.sensor.{type1}",'
    f'"android.sensor.{type2}",'
    f'"android.sensor.{type3}",'
    f'"android.sensor.{type4}",'
    f'"android.sensor.{type5}",'
    f'"android.sensor.{type6}",'
    f'"android.sensor.{type7}",'
    f'"android.sensor.{type8}"'
    f']'
)

connect(url)