# panel serve dashboard_panel.py --autoreload --show


import socket
import threading
from datetime import datetime, timedelta
from collections import deque
import pandas as pd
import numpy as np

import panel as pn
import holoviews as hv
from bokeh.models.formatters import DatetimeTickFormatter

hv.extension('bokeh')
pn.extension()

# === CONFIGURAÇÕES ===
HOST = '127.0.0.1'
PORT = 65431
FREQ_ATUALIZACAO_MS = 100  # Atualização a cada 1 segundo

# === INICIALIZA O BUFFER COMPARTILHADO NO CACHE ===
if 'buffer_dados' not in pn.state.cache:
    pn.state.cache['buffer_dados'] = deque(maxlen=300)  # ~5 min a 1Hz

buffer_dados = pn.state.cache['buffer_dados']

# === FUNÇÃO DE LEITURA DO SOCKET ===
def receber_dados():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("[Socket] Conectando ao servidor...")
        s.connect((HOST, PORT))
        print("[Socket] Conectado!")
        buffer = ""
        while True:
            data = s.recv(1024)
            if not data:
                break
            buffer += data.decode('utf-8')
            linhas = buffer.split('\n')
            buffer = linhas[-1]  # mantém o resto da última linha

            for linha in linhas[:-1]:
                try:
                    if len(linha.strip()) == 0:
                        continue
                    partes = linha.strip().split(',')
                    if len(partes) != 4:
                        print(f"[Ignorado] Linha malformada: {linha}")
                        continue
                    t, hs, tp, dp = partes
                    registro = {
                        'timestamp': pd.to_datetime(t),
                        'Hs': float(hs),
                        'Tp': float(tp),
                        'Dp': float(dp)
                    }
                    pn.state.cache['buffer_dados'].append(registro)
                    print(f"[Adicionado] {registro}")
                except Exception as e:
                    print(f"[Erro] {linha} -> {e}")

# === INICIA A THREAD UMA ÚNICA VEZ ===
if 'socket_thread' not in pn.state.cache:
    thread = threading.Thread(target=receber_dados, daemon=True)
    thread.start()
    pn.state.cache['socket_thread'] = thread
    print("[Thread] Iniciada")

# === FUNÇÕES DE VISUALIZAÇÃO ===

def gerar_df():
    df = pd.DataFrame(pn.state.cache['buffer_dados'])
    if df.empty or 'timestamp' not in df.columns:
        return pd.DataFrame()
    agora = datetime.now()
    return df[df['timestamp'] >= agora - timedelta(seconds=30)]

def plot_hs(df):
    if df.empty:
        return hv.Curve([]).opts(title="Aguardando dados...")
    curva = hv.Curve(df, kdims='timestamp', vdims='Hs').opts(
        height=300, width=800, tools=['hover'],
        title="Altura Significativa (Hs) - Últimos 30s",
        xlabel="Tempo", ylabel="Hs (m)",
        responsive=True, xrotation=45
    )
    return curva

def plot_rosa(df):
    if df.empty:
        return hv.Text(0, 0, "Aguardando dados...")
    bins = np.arange(0, 361, 30)
    df['dir_bin'] = pd.cut(df['Dp'], bins=bins, labels=bins[:-1], include_lowest=True)
    rosa = df.groupby('dir_bin')['Hs'].mean().reset_index()
    rosa['dir_bin'] = rosa['dir_bin'].astype(float)
    bars = hv.BarPolar((rosa['dir_bin'], rosa['Hs']), kdims='dir_bin', vdims='Hs').opts(
        start_angle=90, direction='clockwise', color='Hs', cmap='Viridis',
        line_color='black', padding=0.1, height=400, width=400,
        title='Rosa de Direção com Hs'
    )
    return bars

def gerar_estatisticas(df):
    if df.empty:
        return pn.pane.Markdown("**Aguardando dados...**")
    stats = {
        "Média Hs (m)": round(df["Hs"].mean(), 2),
        "Máx Hs (m)": round(df["Hs"].max(), 2),
        "Min Hs (m)": round(df["Hs"].min(), 2),
        "Std Hs": round(df["Hs"].std(), 2),
        "Última leitura": df["timestamp"].max().strftime('%H:%M:%S')
    }
    return pn.widgets.DataFrame(pd.DataFrame(stats, index=[""]), width=500)

# === PAINÉIS ===

grafico_hs_pane = pn.panel(hv.Curve([]))
grafico_rosa_pane = pn.panel(hv.Text(0, 0, "Aguardando rosa..."))
tabela_stats_pane = pn.panel(pn.Spacer())

def atualizar():
    df = gerar_df()
    grafico_hs_pane.object = plot_hs(df)
    grafico_rosa_pane.object = plot_rosa(df)
    tabela_stats_pane.object = gerar_estatisticas(df)

pn.state.add_periodic_callback(atualizar, period=FREQ_ATUALIZACAO_MS)

# === DASHBOARD FINAL ===

dashboard = pn.Column(
    "## 🌊 Dashboard de Ondas em Tempo Real",
    grafico_hs_pane,
    pn.Row(grafico_rosa_pane, tabela_stats_pane)
)

dashboard.servable()
