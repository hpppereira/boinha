# como rodar:
# panel serve dashboard.py --autoreload


import os
import panel as pn
import pandas as pd
import numpy as np
import holoviews as hv
import time
from datetime import datetime, timedelta

pn.extension('tabulator')
hv.extension('bokeh')

# Simulador: cria/atualiza CSV continuamente (apenas para teste)
csv_path = 'dados.csv'
if not os.path.exists(csv_path):
    df_init = pd.DataFrame({
        'timestamp': pd.date_range(end=datetime.now(), periods=60, freq='S'),
        'valor': np.random.randn(60)
    })
    df_init.to_csv(csv_path, index=False)


while True:
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    novo_valor = {
        'timestamp': datetime.now(),
        'valor': np.random.randn()
    }
    df = df.append(novo_valor, ignore_index=True)
    df.to_csv(csv_path, index=False)
    time.sleep(1)
        
    # Função para ler e filtrar os últimos 30s de dados
    def ler_dados_csv():
        df = pd.read_csv(csv_path, parse_dates=['timestamp'])
        agora = datetime.now()
        janela_inicio = agora - timedelta(seconds=30)
        df = df[df['timestamp'] >= janela_inicio]
        return df

    # Plot interativo com janela deslizante
    def gerar_plot(df):
        curve = hv.Curve(df, kdims='timestamp', vdims='valor').opts(
            height=300, width=800, title="Série Temporal (últimos 30s)",
            tools=['hover'], line_width=2
        )
        return curve

    # Estatísticas atualizadas
    def gerar_tabela_estatisticas(df):
        stats = {
            'Média': [df['valor'].mean()],
            'Desvio Padrão': [df['valor'].std()],
            'Máximo': [df['valor'].max()],
            'Mínimo': [df['valor'].min()],
            'Nº Amostras': [len(df)]
        }
        return pn.widgets.Tabulator(pd.DataFrame(stats), show_index=False)

    # Elementos do dashboard
    plot_painel = pn.panel(hv.Curve([]))
    tabela_painel = pn.panel(pn.Spacer(height=100))

    # Callback periódico
    def atualizar_dashboard():
        df = ler_dados_csv()
        plot_painel.object = gerar_plot(df)
        tabela_painel.object = gerar_tabela_estatisticas(df)

    # Atualizar a cada 2 segundos
    pn.state.add_periodic_callback(atualizar_dashboard, period=2000)

    # Layout
    dashboard = pn.Column(
        "# Dashboard em Tempo Real",
        plot_painel,
        "## Estatísticas da Janela Atual",
        tabela_painel
    )

dashboard.servable()
