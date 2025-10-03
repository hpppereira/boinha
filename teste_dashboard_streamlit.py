# para rodar o painel
# streamlit run dashboard_streamlit.py

# dashboard_streamlit.py

import socket
import pandas as pd
import streamlit as st
import threading
from datetime import datetime, timedelta
from collections import deque
import plotly.express as px
import plotly.graph_objects as go
import time

# Configurações
HOST = '127.0.0.1'
PORT = 65431

# Dados em buffer com janela móvel (~5 minutos, 1Hz)
buffer_dados = deque(maxlen=300)

# Função para ler do socket
def receber_dados():
    global buffer_dados
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        buffer = ""
        while True:
            data = s.recv(1024)
            if not data:
                break
            buffer += data.decode('utf-8')
            linhas = buffer.split('\n')
            # buffer = linhas[-2]
            for linha in linhas[:-1]:
                print (linha)
                if len(linha.split(',')) < 4:
                        print ('aa')
                        pass
                else:
                    t, hs, tp, dp = linha.strip().split(',')
                    buffer_dados.append({
                        'timestamp': pd.to_datetime(t),
                        'Hs': float(hs),
                        'Tp': float(tp),
                        'Dp': float(dp)
                    })

# Iniciar thread do socket (só uma vez)
if 'socket_thread' not in st.session_state:
    thread = threading.Thread(target=receber_dados, daemon=True)
    thread.start()
    st.session_state.socket_thread = True

# Título
st.title("🌊 Dashboard de Ondas em Tempo Real")

time.sleep(10)

# Obter dados dos últimos 30 segundos
df = pd.DataFrame(buffer_dados)
agora = datetime.now()
inicio = agora - timedelta(seconds=30)
df = df[df['timestamp'] >= inicio]

if df.empty:
    st.warning("Aguardando dados do servidor...")
    st.stop()

# Série Temporal - Hs
fig_hs = px.line(df, x='timestamp', y='Hs', title='Altura Significativa (Hs)', markers=True)
st.plotly_chart(fig_hs, use_container_width=True)

# Rosa de Direção - Dp vs Hs
fig_rosa = go.Figure()
bins_dir = list(range(0, 361, 30))

# Agrupa por direção
df['dir_bin'] = pd.cut(df['Dp'], bins=bins_dir, include_lowest=True)
df_agg = df.groupby('dir_bin')['Hs'].mean().reset_index()
df_agg['dir_centro'] = df_agg['dir_bin'].apply(lambda x: x.mid)

fig_rosa.add_trace(go.Barpolar(
    r=df_agg['Hs'],
    theta=df_agg['dir_centro'],
    width=[30]*len(df_agg),
    marker_color=df_agg['Hs'],
    marker_colorscale='Viridis',
    opacity=0.8
))

fig_rosa.update_layout(
    title="🌪 Rosa de Direção com Altura Significativa (Hs)",
    polar=dict(
        angularaxis=dict(direction='clockwise', rotation=90),
        radialaxis=dict(range=[0, df_agg['Hs'].max() + 0.5])
    )
)

st.plotly_chart(fig_rosa, use_container_width=True)

# Estatísticas
st.subheader("📊 Estatísticas dos Últimos 30s")
col1, col2, col3 = st.columns(3)
col1.metric("Média Hs (m)", f"{df['Hs'].mean():.2f}")
col2.metric("Máximo Hs (m)", f"{df['Hs'].max():.2f}")
col3.metric("N Amostras", len(df))
