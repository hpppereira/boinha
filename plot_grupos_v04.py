import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from collections import deque
from matplotlib.animation import FuncAnimation
import matplotlib.cm as cm

# ----------------- CONFIG -----------------
FREQ_AQUISICAO = 1        # Hz
JANELA_SEGUNDOS = 300     # 5 minutos
N_PONTOS = JANELA_SEGUNDOS * FREQ_AQUISICAO
THRESHOLD_PERCENTIL = 25
DURACAO_MINIMA_GRUPO = 30  # s
ARQUIVO = 'data/2021-05-28T06h00.raw'

# ----------------- CARREGA DADOS -----------------
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
texto_stats = ax.text(0.02, 0.95, '', transform=ax.transAxes,
                      fontsize=10, verticalalignment='top')

ax.set_xlim(0, JANELA_SEGUNDOS)
ax.set_ylim(-2, 2)
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Amplitude (m)")
ax.legend()
ax.grid(True)

# ----------------- FUNÇÃO DE CÁLCULO DOS GRUPOS -----------------
def calcula_grupos(signal, fs=1, threshold_percentile=25):
    """Cálculo de grupos via cruzamentos do envelope e retorno de propriedades."""
    if len(signal) < 2:
        return {"envelope": np.array([]), "mascara": np.array([], dtype=bool), "grupos": [], "limiar": 0.0}

    # Envelope via Hilbert
    analytic = hilbert(signal)
    envelope = np.abs(analytic)
    limiar = np.percentile(envelope, threshold_percentile)

    acima = envelope > limiar
    cruzou = np.diff(acima.astype(int))

    inicios = np.where(cruzou == 1)[0]
    fins = np.where(cruzou == -1)[0]

    if fins.size and inicios.size and fins[0] < inicios[0]:
        fins = fins[1:]
    if inicios.size and (not fins.size or inicios[-1] > fins[-1]):
        fins = np.append(fins, len(envelope) - 1)

    grupos = []
    mascara = np.zeros_like(envelope, dtype=bool)

    for i in range(len(inicios)):
        ini, fim = inicios[i], fins[i]
        duracao = (fim - ini) / fs
        if duracao < DURACAO_MINIMA_GRUPO:
            continue  # ignora grupos curtos

        mascara[ini:fim] = True
        trecho = signal[ini:fim]

        # Altura significativa do grupo (4 * std)
        Hs = 4 * np.std(trecho) if len(trecho) > 1 else 0

        grupos.append({
            "ini": ini,
            "fim": fim,
            "duracao": duracao,
            "Hs": Hs
        })

    return {"envelope": envelope, "mascara": mascara, "grupos": grupos, "limiar": limiar}

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

    # Remove áreas e textos anteriores
    while ax.collections:
        ax.collections[-1].remove()
    [txt.remove() for txt in ax.texts if txt not in [texto_stats]]

    # Gradiente de cor baseado na duração
    duracoes = [g["duracao"] for g in stats["grupos"]] if stats["grupos"] else [0]
    if duracoes:
        dur_max = max(duracoes) or 1
        cmap = cm.get_cmap('magma')

    # Preenche grupos válidos
    for i, g in enumerate(stats["grupos"]):
        cor = cmap(g["duracao"] / dur_max)
        ax.fill_between(
            t_rel[g["ini"]:g["fim"]],
            ax.get_ylim()[0],
            ax.get_ylim()[1],
            color=cor,
            alpha=0.25
        )
        # Adiciona rótulo na parte inferior do gráfico
        t_centro = (t_rel[g["ini"]] + t_rel[g["fim"]]) / 2
        y_txt = ax.get_ylim()[0] + 0.1  # parte de baixo
        ax.text(t_centro, y_txt,
                f"G{i+1}\nHs={g['Hs']:.2f} m",
                ha='center', va='bottom',
                fontsize=9, color='black')

    # Linha do limiar
    global ax_limiar
    if ax_limiar:
        ax_limiar.remove()
    ax_limiar = ax.axhline(stats["limiar"], color='gray', linestyle='--', alpha=0.5)

    # Estatísticas gerais
    n = len(stats["grupos"])
    dur_med = np.mean([g["duracao"] for g in stats["grupos"]]) if n else 0
    Hs_med = np.mean([g["Hs"] for g in stats["grupos"]]) if n else 0
    texto_stats.set_text(
        f"Nº grupos (>30s): {n}\nDur. média: {dur_med:.1f} s\nHs médio: {Hs_med:.2f} m"
    )

    return linha_heave, linha_envelope, texto_stats

# ----------------- ANIMAÇÃO -----------------
ani = FuncAnimation(fig, atualizar, frames=range(N_TOTAL), interval=100, blit=False, repeat=False)
plt.tight_layout()
plt.show()
