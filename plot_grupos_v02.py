import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from collections import deque
from matplotlib.animation import FuncAnimation

# ----------------- CONFIG -----------------
FREQ_AQUISICAO = 1        # Hz (1 amostra por segundo)
JANELA_SEGUNDOS = 300     # 5 minutos
N_PONTOS = JANELA_SEGUNDOS * FREQ_AQUISICAO
THRESHOLD_PERCENTIL = 50  # percentil para detectar grupos
ARQUIVO = 'data/2021-05-28T06h00.raw'  # arquivo de exemplo

# ----------------- CARREGA DADOS (SIMULA STREAM) -----------------
df = pd.read_csv(ARQUIVO, header=None)
heave_data = df[1].values / 100.0
N_TOTAL = len(heave_data)

# ----------------- BUFFERS -----------------
buffer_tempo = deque(maxlen=N_PONTOS)
buffer_heave = deque(maxlen=N_PONTOS)

# ----------------- FIGURA -----------------
fig, ax = plt.subplots(figsize=(12, 5))
linha_heave, = ax.plot([], [], label='Heave [m]', color='blue')
linha_envelope, = ax.plot([], [], label='Envelope', color='orange')
ax_limiar = None
texto_stats = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top')

ax.set_xlim(0, JANELA_SEGUNDOS)
ax.set_ylim(-2, 2)
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Amplitude (m)")
ax.legend()
ax.grid(True)

# ----------------- FUNÇÃO DE CÁLCULO DOS GRUPOS -----------------
def calcula_grupos(signal, fs=1, threshold_percentile=25):
    """Cálculo de grupos via cruzamentos do envelope."""
    if len(signal) < 2:
        return {
            "envelope": np.array([]),
            "mascara": np.array([], dtype=bool),
            "num_grupos": 0,
            "duracao_media": 0.0,
            "intervalo_medio": 0.0,
            "limiar": 0.0
        }

    # Envelope via Hilbert
    analytic = hilbert(signal)
    envelope = np.abs(analytic)
    limiar = np.percentile(envelope, threshold_percentile)

    # Cruzamentos do envelope com o limiar
    acima = envelope > limiar
    cruzou = np.diff(acima.astype(int))

    # Inícios e fins de grupos
    inicios = np.where(cruzou == 1)[0]
    fins = np.where(cruzou == -1)[0]

    if fins.size and inicios.size and fins[0] < inicios[0]:
        fins = fins[1:]
    if inicios.size and (not fins.size or inicios[-1] > fins[-1]):
        fins = np.append(fins, len(envelope) - 1)

    duracoes, intervalos = [], []
    for i in range(len(inicios)):
        t_ini = inicios[i] / fs
        t_fim = fins[i] / fs if i < len(fins) else inicios[i] / fs
        duracoes.append(t_fim - t_ini)
        if i > 0:
            t_fim_ant = fins[i - 1] / fs
            intervalos.append(t_ini - t_fim_ant)

    mascara = np.zeros_like(envelope, dtype=bool)
    for i in range(len(inicios)):
        fim = fins[i] if i < len(fins) else inicios[i]
        mascara[inicios[i]:fim] = True

    stats = {
        "envelope": envelope,
        "mascara": mascara,
        "num_grupos": len(inicios),
        "duracao_media": np.mean(duracoes) if duracoes else 0.0,
        "intervalo_medio": np.mean(intervalos) if intervalos else 0.0,
        "limiar": limiar
    }
    return stats

# ----------------- FUNÇÃO DE ATUALIZAÇÃO -----------------
def atualizar(frame):
    if frame >= N_TOTAL:
        return linha_heave, linha_envelope, texto_stats

    heave_valor = float(heave_data[frame])
    t = frame / FREQ_AQUISICAO
    buffer_tempo.append(t)
    buffer_heave.append(heave_valor)

    tempo = np.array(buffer_tempo)
    dados = np.array(buffer_heave)

    stats = calcula_grupos(dados, fs=FREQ_AQUISICAO, threshold_percentile=THRESHOLD_PERCENTIL)
    t_rel = tempo - tempo[0] if len(tempo) > 0 else tempo

    linha_heave.set_data(t_rel, dados)
    linha_envelope.set_data(t_rel, stats["envelope"])
    ax.set_xlim(0, max(JANELA_SEGUNDOS, t_rel[-1]))

    # Limpa áreas anteriores (preenchimentos)
    while ax.collections:
        ax.collections[-1].remove()

    # Preenche regiões onde envelope > limiar (grupos)
    if stats["mascara"].size:
        ax.fill_between(
            t_rel,
            ax.get_ylim()[0],
            ax.get_ylim()[1],
            where=stats["mascara"],
            color='red',
            alpha=0.1
        )

    # Desenha linha de limiar no envelope
    global ax_limiar
    if ax_limiar:
        ax_limiar.remove()
    ax_limiar = ax.axhline(stats["limiar"], color='gray', linestyle='--', alpha=0.5)

    # Atualiza estatísticas
    texto_stats.set_text(
        f"Nº grupos: {stats['num_grupos']}\n"
        f"Dur. média: {stats['duracao_media']:.1f} s\n"
        f"Int. médio: {stats['intervalo_medio']:.1f} s"
    )

    return linha_heave, linha_envelope, texto_stats

# ----------------- ANIMAÇÃO -----------------
ani = FuncAnimation(fig, atualizar, frames=range(N_TOTAL), interval=100, blit=False, repeat=False)
plt.tight_layout()
plt.show()
