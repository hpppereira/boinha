import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy.ndimage import label
from collections import deque
from matplotlib.animation import FuncAnimation

# ----------------- CONFIG -----------------
FREQ_AQUISICAO = 1        # Hz (1 amostra por segundo)
JANELA_SEGUNDOS = 300     # 5 minutos
N_PONTOS = JANELA_SEGUNDOS * FREQ_AQUISICAO
THRESHOLD_PERCENTIL = 25  # percentil para detectar grupos
ARQUIVO = 'data/2021-05-28T06h00.raw'  # arquivo de exemplo

# ----------------- CARREGA DADOS (SIMULA STREAM) -----------------
df = pd.read_csv(ARQUIVO, header=None)
heave_data = df[1].values / 100.0  # transformar para metros, se aplicável
N_TOTAL = len(heave_data)

# ----------------- BUFFERS -----------------
buffer_tempo = deque(maxlen=N_PONTOS)
buffer_heave = deque(maxlen=N_PONTOS)

# ----------------- FIGURA -----------------
fig, ax = plt.subplots(figsize=(12, 5))
linha_heave, = ax.plot([], [], label='Heave [m]')
linha_envelope, = ax.plot([], [], label='Envelope')
texto_stats = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=10, verticalalignment='top')

ax.set_xlim(0, JANELA_SEGUNDOS)
ax.set_ylim(-2, 2)
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Amplitude (m)")
ax.legend()
ax.grid(True)

# ----------------- FUNÇÕES -----------------
def calcula_grupos(signal, fs=1, threshold_percentile=25):
    """Retorna envelope, máscara de grupos, e estatísticas básicas."""
    if len(signal) == 0:
        return {
            "envelope": np.array([]),
            "mascara": np.array([], dtype=bool),
            "num_grupos": 0,
            "duracao_media": 0.0,
            "intervalo_medio": 0.0
        }

    analytic = hilbert(signal)
    envelope = np.abs(analytic)
    limiar = np.percentile(envelope, threshold_percentile)
    mascara = envelope > limiar

    labels, num_grupos = label(mascara)
    duracoes, intervalos = [], []
    fim_anterior = None
    for i in range(1, num_grupos + 1):
        idx = np.where(labels == i)[0]
        t_ini = idx[0] / fs
        t_fim = idx[-1] / fs
        duracoes.append(t_fim - t_ini)
        if fim_anterior is not None:
            intervalos.append(t_ini - fim_anterior)
        fim_anterior = t_fim

    stats = {
        "envelope": envelope,
        "mascara": mascara,
        "num_grupos": int(num_grupos),
        "duracao_media": float(np.mean(duracoes)) if duracoes else 0.0,
        "intervalo_medio": float(np.mean(intervalos)) if intervalos else 0.0
    }
    return stats

def calcula_grupos1(signal, fs=1, threshold_percentile=25):
    """
    Calcula parâmetros de grupos com base nos cruzamentos do envelope de Hilbert.
    """
    if len(signal) < 2:
        return {
            "envelope": np.array([]),
            "mascara": np.array([], dtype=bool),
            "num_grupos": 0,
            "duracao_media": 0.0,
            "intervalo_medio": 0.0
        }

    # --- Envelope via Hilbert ---
    analytic = hilbert(signal)
    envelope = np.abs(analytic)

    # --- Limiar baseado em percentil (ou valor fixo, se quiser testar) ---
    limiar = np.percentile(envelope, threshold_percentile)

    # --- Identificar cruzamentos ---
    acima = envelope > limiar
    cruzou = np.diff(acima.astype(int))

    # Índices de subida (início de grupo) e descida (fim de grupo)
    inicios = np.where(cruzou == 1)[0]
    fins = np.where(cruzou == -1)[0]

    # Ajuste caso série comece ou termine dentro de um grupo
    if fins.size and inicios.size and fins[0] < inicios[0]:
        fins = fins[1:]
    if inicios.size and (not fins.size or inicios[-1] > fins[-1]):
        fins = np.append(fins, len(envelope) - 1)

    # --- Calcular durações e intervalos ---
    duracoes = []
    intervalos = []
    for i in range(len(inicios)):
        t_ini = inicios[i] / fs
        t_fim = fins[i] / fs if i < len(fins) else inicios[i] / fs
        duracoes.append(t_fim - t_ini)
        if i > 0:
            t_fim_ant = fins[i - 1] / fs
            intervalos.append(t_ini - t_fim_ant)

    num_grupos = len(duracoes)
    duracao_media = np.mean(duracoes) if duracoes else 0.0
    intervalo_medio = np.mean(intervalos) if intervalos else 0.0

    # --- Construir máscara booleana para plot ---
    mascara = np.zeros_like(envelope, dtype=bool)
    for i in range(len(inicios)):
        fim = fins[i] if i < len(fins) else inicios[i]
        mascara[inicios[i]:fim] = True

    stats = {
        "envelope": envelope,
        "mascara": mascara,
        "num_grupos": num_grupos,
        "duracao_media": duracao_media,
        "intervalo_medio": intervalo_medio,
        "limiar": limiar
    }
    return stats


# ----------------- ATUALIZAÇÃO -----------------
def atualizar(frame):
    """
    frame -> índice da amostra no 'stream' simulado (0..N_TOTAL-1)
    """
    # pega o valor 'em tempo real' (simulado) usando o frame
    if frame >= N_TOTAL:
        return linha_heave, linha_envelope, texto_stats  # nada mais a fazer

    heave_valor = float(heave_data[frame])

    # tempo em segundos desde o início do stream (frame/FREQ)
    t = frame / FREQ_AQUISICAO
    buffer_tempo.append(t)
    buffer_heave.append(heave_valor)

    tempo = np.array(buffer_tempo)
    dados = np.array(buffer_heave)

    stats = calcula_grupos(dados, fs=FREQ_AQUISICAO, threshold_percentile=THRESHOLD_PERCENTIL)
    stats = calcula_grupos1(dados, fs=FREQ_AQUISICAO, threshold_percentile=THRESHOLD_PERCENTIL)

    # ajustar linhas
    # mostramos tempo relativo desde o início da janela (0 .. window)
    t_rel = tempo - tempo[0] if len(tempo) > 0 else tempo
    linha_heave.set_data(t_rel, dados)
    linha_envelope.set_data(t_rel, stats["envelope"])

    # eixo x: mostre toda a janela atual (até JANELA_SEGUNDOS)
    xmax = max(JANELA_SEGUNDOS, t_rel[-1]) if len(t_rel) > 0 else JANELA_SEGUNDOS
    ax.set_xlim(0, xmax)

    # remover preenchimentos anteriores (regiões de grupo)
    # ax.collections guarda os fill_between
    while ax.collections:
        ax.collections[-1].remove()

    # desenhar preenchimento de grupos (se houver)
    if stats["mascara"].size:
        # a máscara corresponde aos índices do vetor 'dados'
        ax.fill_between(t_rel, ax.get_ylim()[0], ax.get_ylim()[1],
                        where=stats["mascara"], interpolate=True, alpha=0.12, color='red')

    # atualizar texto de estatísticas
    texto_stats.set_text(
        f"Nº grupos: {stats['num_grupos']}\n"
        f"Dur. média: {stats['duracao_media']:.1f} s\n"
        f"Int. médio: {stats['intervalo_medio']:.1f} s"
    )

    # retorno dos artistas (importante se usar blit=True)
    return linha_heave, linha_envelope, texto_stats

# ----------------- RODAR ANIMAÇÃO -----------------
# frames: usa todos os índices das amostras (1 por segundo)
ani = FuncAnimation(fig, atualizar, frames=range(N_TOTAL), interval=200, blit=True, repeat=False)

plt.tight_layout()
plt.show()
