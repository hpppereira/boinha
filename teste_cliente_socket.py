# cliente_socket.py

import socket
import pandas as pd
from io import StringIO

HOST = 'localhost'
PORT = 65432

dados = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("Conectado ao servidor...")
    buffer = ""
    while True:
        data = s.recv(1024)
        if not data:
            break
        buffer += data.decode('utf-8')
        linhas = buffer.split('\n')
        buffer = linhas[-1]  # última linha pode estar incompleta
        for linha in linhas[:-1]:
            try:
                timestamp_str, valor_str = linha.split(',')
                dados.append({'timestamp': pd.to_datetime(timestamp_str), 'valor': float(valor_str)})
            except:
                continue  # ignora erros de parsing

        # Mostra os 5 últimos valores recebidos
        df = pd.DataFrame(dados)
        print(df.tail())
