import os
import numpy as np
import librosa
from sklearn.preprocessing import LabelEncoder

DATASET_PATH = "Dataset-comandos-voz"
SR = 22050
FAIXAS_FREQUENCIA = [
    (150, 300), (300, 450), (450, 600), (600, 750), (750, 900),
    (900, 1050), (1050, 1200), (1200, 1350), (1350, 1500),
    (1500, 1650), (1650, 1800), (1800, 1950), (1950, 2100)
]
CLASSES = ['Brincar', 'Comer', 'Corrida', 'Entrar', 'Partida', 'Procurar', 'Sair', 'Testar']

def add_noise(y, noise_factor=0.005):
    noise = np.random.randn(len(y))
    return y + noise_factor * noise

def pitch_shift(y, sr, n_steps=2):
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps)

def time_stretch(y, rate=1.1):
    return librosa.effects.time_stretch(y, rate=rate)

def extrair_features(canal):
    canal = canal * np.hanning(len(canal))
    N = len(canal)
    Y = np.abs(np.fft.fft(canal))[:N // 2]
    freqs = np.fft.fftfreq(N, d=1 / SR)[:N // 2]

    vetor = []
    for (f_min, f_max) in FAIXAS_FREQUENCIA:
        idx = np.where((freqs >= f_min) & (freqs < f_max))[0]
        faixa = Y[idx]
        if len(faixa) > 0:
            vetor.append(np.max(faixa))
            vetor.append(np.mean(faixa))
            vetor.append(np.std(faixa))
        else:
            vetor.extend([0.0, 0.0, 0.0])
    return vetor

X = []
y = []

print(" Processando áudios com augmentação...")

for classe in CLASSES:
    pasta = os.path.join(DATASET_PATH, classe)
    for arquivo in os.listdir(pasta):
        if not arquivo.endswith(".wav"):
            continue

        caminho = os.path.join(pasta, arquivo)
        sinal, sr = librosa.load(caminho, sr=SR, mono=False)

        if len(sinal.shape) == 1:
            sinal = np.stack([sinal, sinal], axis=0)

        sinais = [sinal]

        for canal in sinal:
            sinais.extend([
                np.stack([add_noise(canal), add_noise(canal)]),
                np.stack([pitch_shift(canal, SR), pitch_shift(canal, SR)]),
                np.stack([time_stretch(canal, rate=1.05), time_stretch(canal, rate=1.05)])
            ])

        for sinal_aug in sinais:
            for canal in sinal_aug:
                feat = extrair_features(canal)
                X.append(feat)
                y.append(classe)

print(f" Total de amostras processadas (com augmentação): {len(X)}")

le = LabelEncoder()
y_encoded = le.fit_transform(y)

os.makedirs("features", exist_ok=True)
np.save("features/X_fft_aug.npy", np.array(X))
np.save("features/y_labels_aug.npy", np.array(y_encoded))
print(" Arquivos salvos em features/X_fft_aug.npy e y_labels_aug.npy")
