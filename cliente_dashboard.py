# cliente_dashboard.py
import socket
import threading
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque

import panel as pn
import holoviews as hv

pn.extension('tabulator')
hv.extension('bokeh')

HOST = 'localhost'
PORT = 65432

# Buffer de dados (janela deslizante)
buffer_dados = deque(maxlen=300)  # ~5 minutos se 1Hz

# Função para receber dados via socket em background
def receber_dados():
    global buffer_dados
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("[Cliente] Conectando...")
        s.connect((HOST, PORT))
        print("[Cliente] Conectado!")
        buffer = ""
        while True:
            data = s.recv(1024)
            if not data:
                break
            buffer += data.decode('utf-8')
            linhas = buffer.split('\n')
            buffer = linhas[-1]
            for linha in linhas[:-1]:
                try:
                    t, hs, tp, dp = linha.strip().split(',')
                    buffer_dados.append({
                        'timestamp': pd.to_datetime(t),
                        'Hs': float(hs),
                        'Tp': float(tp),
                        'Dp': float(dp)
                    })
                except Exception as e:
                    print(f"[Erro parsing] {linha} - {e}")

# Iniciar thread de recebimento
thread = threading.Thread(target=receber_dados, daemon=True)
thread.start()

# Funções do dashboard
def gerar_df():
    agora = datetime.now()
    inicio = agora - timedelta(seconds=30)
    df = pd.DataFrame(buffer_dados)
    if not df.empty:
        df = df[df['timestamp'] >= inicio]
    return df

def plot_hs(df):
    return hv.Curve(df, kdims='timestamp', vdims='Hs').opts(
        title='Altura Significativa (Hs)', height=300, width=800, tools=['hover'])

def tabela_estat(df):
    if df.empty:
        return pn.pane.Markdown("**Aguardando dados...**")
    stats = {
        'Média Hs (m)': [df['Hs'].mean()],
        'Máximo Hs (m)': [df['Hs'].max()],
        'Mínimo Hs (m)': [df['Hs'].min()],
        'Desvio Padrão Hs': [df['Hs'].std()],
        'Última Leitura': [df['timestamp'].max()]
    }
    return pn.widgets.Tabulator(pd.DataFrame(stats), show_index=False)

# Elementos do painel
plot_pane = pn.panel(hv.Curve([]))
tabela_pane = pn.panel(pn.Spacer())

# Atualizador periódico
def atualizar():
    df = gerar_df()
    plot_pane.object = plot_hs(df)
    tabela_pane.object = tabela_estat(df)

pn.state.add_periodic_callback(atualizar, period=2000)

# Layout do dashboard
dashboard = pn.Column(
    "# 🌊 Dashboard de Ondas em Tempo Real",
    plot_pane,
    "## 📊 Estatísticas dos últimos 30s",
    tabela_pane
)

dashboard.servable()
