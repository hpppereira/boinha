# servidor_socket.py

import socket
import time
import numpy as np
from datetime import datetime

HOST = '0.0.0.0'
PORT = 65431

def gerar_parametros_onda():
    timestamp = datetime.now().isoformat()
    Hs = np.random.uniform(0.5, 3.0)
    Tp = np.random.uniform(5, 15)
    Dp = np.random.uniform(0, 360)
    return f"{timestamp},{Hs:.2f},{Tp:.2f},{Dp:.1f}\n"

def gerar_serie_onda(t):
    timestamp = datetime.now().isoformat()
    t = 0
    DT = 0.2
    Hs = 3.0
    Tp = 10.0
    A = Hs / 2.0
    w = 2 * np.pi / Tp
    heave = A * np.sin(w * t)
    pitch = 2 * np.degrees(np.gradient([A * np.sin(w * s) for s in np.linspace(t - DT, t + DT, 3)], DT))[1]
    roll = 2 * np.degrees(np.gradient([0.5 * A * np.sin(w * s + np.pi / 3) for s in np.linspace(t - DT, t + DT, 3)], DT))[1]
    return f"{timestamp},{heave:.2f},{pitch:.2f},{roll:.2f}\n"

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"[Servidor] Escutando em {HOST}:{PORT}...")
    conn, addr = s.accept()
    with conn:
        print(f"[Servidor] Conectado por {addr}")
        # t = 0
        while True:
            # t += 1
            dado = gerar_parametros_onda()
            # dado = gerar_serie_onda(t)
            print(f"[Servidor] Enviando: {dado.strip()}")
            try:
                conn.sendall(dado.encode('utf-8'))
            except BrokenPipeError:
                print("[Servidor] Cliente desconectado.")
                break
            time.sleep(1)
