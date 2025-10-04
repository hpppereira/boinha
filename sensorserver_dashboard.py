#!/work/projetos/projeto-oceanpact_surf/venv/bin/python

"""
Dashboard para Boias de Ondas
Monitoramento em tempo real dos dados oceanográficos
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import threading
import time
from random import random
from pathlib import Path

app = Flask(__name__)
CORS(app)


# user = str(Path.home()).split('/')[2]

# Caminho para o arquivo CSV
# CSV_PATH = 'wave_data.csv'
# pth_out = f'/mnt/c/Users/{user}/OneDrive - atmosmarine.com/AtmosMarine/03_Projetos/CC25011_OCEANPACT_Surf/out/heave/api/'
pth_out = 'data/'
fln = 'param_boinha'

# boia = '6613'

CSV_PATH = os.path.join(pth_out, f'{fln}.csv')
# CSV_PATH = 'out/op_param_obscape_6613.csv'

def read_wave_data():
    """Lê os dados do CSV e retorna um DataFrame"""
    try:
        df = pd.read_csv(CSV_PATH)
        df = df.iloc[-30:]
        # df = df.loc['2025-08-06':]

        # vv = ['hm0', 'fp', 'tp', 'tm02', 'tm', 'v', 'Qp', 'L0', 'k0', 'BFI', 'm0_hilbert',
        #       'GF_hilbert', 'hs', 'ts', 'h10', 'hmax', 'tz', 'thmax', 'hmaxhs', 'kurt_n',
        #       'skew_n', 'kurt_H', 'skew_H', 'kurt_T', 'skew_T', 'corr_H', 'corr_T', 'nruns']

        # df[vv] = df[vv] * random()
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        print(f"Erro ao ler CSV: {e}")
        return pd.DataFrame()

@app.route('/boinha/api/wave/latest')
def get_latest_data():
    """Retorna as últimas 5 medições"""
    df = read_wave_data()
    if df.empty:
        return jsonify([])
    
    latest = df.tail(10).to_dict('records')
    for record in latest:
        record['date'] = record['date'].strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify(latest)

@app.route('/boinha/api/wave/timeseries')
def get_timeseries_data():
    """Retorna dados para gráficos de séries temporais"""
    df = read_wave_data()
    if df.empty:
        return jsonify({})
    
    data = {
        'dates': df['date'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'hm0': df['hs'].tolist(),
        'hmax': df['hmax'].tolist(),
        'tp': df['ts'].tolist(),
        'thmax': df['thmax'].tolist()
        # 'tm': df['tm'].tolist()
    }
    
    return jsonify(data)

@app.route('/boinha/api/wave/histograms')
def get_histogram_data():
    """Retorna dados para histogramas"""
    df = read_wave_data()
    if df.empty:
        return jsonify({})
    
    def create_histogram(data, bins=10):
        hist, bin_edges = np.histogram(data.dropna(), bins=bins)
        return {
            'counts': hist.tolist(),
            'bin_edges': bin_edges.tolist()
        }
    
    histograms = {
        'hm0': create_histogram(df['hm0']),
        'thmax': create_histogram(df['thmax']),
        'tp': create_histogram(df['tp']),
        # 'tm': create_histogram(df['tm'])
    }
    
    return jsonify(histograms)

@app.route('/boinha/api/wave/stats')
def get_statistics():
    """Retorna estatísticas básicas dos dados"""
    df = read_wave_data()
    if df.empty:
        return jsonify({})
    
    variables = ['hm0', 'thmax', 'tp']
    stats = {}
    
    for var in variables:
        if var in df.columns:
            stats[var] = {
                'mean': float(df[var].mean()),
                'std': float(df[var].std()),
                'min': float(df[var].min()),
                'max': float(df[var].max()),
                'current': float(df[var].iloc[-1]) if len(df) > 0 else 0
            }
    
    return jsonify(stats)

@app.route('/boinha')
@app.route('/boinha/')
def oceanpact_dashboard():
    """Página do dashboard OceanPact"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/')
def dashboard():
    """Página principal do dashboard"""
    return render_template_string(DASHBOARD_HTML)


# HTML do Dashboard

with open('sensorserver_dashboard.html', 'r', encoding='utf-8') as arquivo:
    DASHBOARD_HTML = arquivo.read()

if __name__ == '__main__':
    # Iniciar simulador de dados em thread separada
    # simulator_thread = threading.Thread(target=data_simulator, daemon=True)
    # simulator_thread.start()
    
    print("Dashboard de Boias de Ondas iniciado!")
    print("Acesse: http://localhost:5003")
    print("Pressione Ctrl+C para parar")
    
    app.run(host='0.0.0.0', port=5003, debug=False)

