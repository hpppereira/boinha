import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.ndimage import label
from collections import deque
from matplotlib.animation import FuncAnimation
import time

# --- CARREGAMENTO DOS DADOS ---
df = pd.read_csv('data/2021-05-28T06h00.raw', header=None)
n1 = df[1].values / 100.0

# --- CONFIGURAÇÕES ---
FREQ_AQUISICAO = 1  # Hz
JANELA_SEGUNDOS = 300
N_PONTOS = JANELA_SEGUNDOS * FREQ_AQUISICAO

# --- BUFFER DE DADOS ---
buffer_tempo = deque(maxlen=N_PONTOS)
buffer_heave = deque(maxlen=N_PONTOS)
start_time = time.time()

# --- SETUP DO PLOT ---
fig, ax = plt.subplots(figsize=(12, 5))
linha_heave, = ax.plot([], [], label='Heave')
linha_envelope, = ax.plot([], [], label='Envelope', color='orange')
texto_stats = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top')

ax.set_xlim(0, JANELA_SEGUNDOS)
ax.set_ylim(-2, 2)
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Amplitude (m)")
ax.legend()
ax.grid(True)

# # --- FUNÇÃO DE GERAR DADO ---
# def gerar_heave(n1, t):
#     if t < len(n1):
#         return n1[t]
#     else:
#         return 0.0

# --- FUNÇÃO DE ATUALIZAÇÃO ---
def atualizar(frame):

    tempo_atual = time.time() - start_time
    tempo_atual_int = int(tempo_atual)

    # if tempo_atual_int >= len(n1):
    #     return  # evita erro de index

    # heave_valor = gerar_heave(n1, tempo_atual_int)
    heave_valor = n1[tempo_atual_int]

    buffer_tempo.append(tempo_atual)
    buffer_heave.append(heave_valor)

    tempo = np.array(buffer_tempo)
    dados = np.array(buffer_heave)
    analytic = hilbert(dados)
    envelope = np.abs(analytic)
    threshold = np.percentile(envelope, 25)
    grupos_bool = envelope > threshold

    # --- CÁLCULO DE ESTATÍSTICAS DOS GRUPOS ---
    labels, num_grupos = label(grupos_bool)
    duracoes = []
    intervalos = []
    fim_anterior = None
    for i in range(1, num_grupos + 1):
        idx = np.where(labels == i)[0]
        t_ini = tempo[idx[0]]
        t_fim = tempo[idx[-1]]
        duracoes.append(t_fim - t_ini)
        if fim_anterior is not None:
            intervalos.append(t_ini - fim_anterior)
        fim_anterior = t_fim

    media_duracao = np.mean(duracoes) if duracoes else 0
    media_intervalo = np.mean(intervalos) if intervalos else 0

    # --- ATUALIZAÇÃO DO PLOT ---
    linha_heave.set_data(tempo, dados)
    linha_envelope.set_data(tempo, envelope)
    ax.set_xlim(tempo[0], tempo[-1])

    # Remove preenchimentos anteriores
    while ax.collections:
        ax.collections[-1].remove()

    ax.fill_between(tempo, -2, 2, where=grupos_bool, color='red', alpha=0.1)

    texto_stats.set_text(
        f"Nº grupos: {num_grupos}\n"
        f"Dur. média: {media_duracao:.1f} s\n"
        f"Int. médio: {media_intervalo:.1f} s"
    )

# --- ANIMAÇÃO ---
ani = FuncAnimation(fig, atualizar, interval=FREQ_AQUISICAO)  # ~1.28 Hz
plt.tight_layout()
plt.show()
