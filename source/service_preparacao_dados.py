import numpy as np
import os

from service_fft import analisar_som_fourier

def load_and_extract_features(audio_dir, labels_map):
    """
    Carrega arquivos de áudio de um diretório, extrai características
    e prepara os dados X e y.

    Args:
        audio_dir (str): Caminho para o diretório contendo subpastas com áudios rotulados.
                         Ex: audio_dir/Brincar/audio1.wav, audio_dir/Comer/audio2.wav
        labels_map (dict): Um mapeamento de nomes de classe para índices numéricos.
                           Ex: {'Brincar': 0, 'Comer': 1, ...}

    Returns:
        tuple: (X, y) onde X é a matriz de características e y são os rótulos numéricos.
    """
    X_features = []
    y_labels = []

    for label_name, label_id in labels_map.items():
        class_dir = os.path.join(audio_dir, label_name)
        if not os.path.isdir(class_dir):
            print(f"Aviso: Diretório da classe '{label_name}' não encontrado: {class_dir}")
            continue

        for filename in os.listdir(class_dir):
            if filename.endswith(".wav"):  # Você pode adicionar outros formatos se suportados por soundfile
                file_path = os.path.join(class_dir, filename)
                features = analisar_som_fourier(file_path)  # Usando a função de análise de áudio

                if "erro" in features:
                    print(f"Erro ao processar {file_path}: {features['erro']}")
                    continue

                # Coleta as características em uma lista ordenada
                feature_vector = [
                    features['pico_frequencia'],
                    features['pico_amplitude'],
                    features['energia_total'],
                    features['media_abs'],
                    features['centroide_espectral'],
                    features['largura_banda_espectral'],
                    features['zcr']
                ]
                X_features.append(feature_vector)
                y_labels.append(label_id)

    return np.array(X_features), np.array(y_labels)


def train_test_split_custom(X, y, test_size=0.2, random_state=None):
    """
    Divide os dados em conjuntos de treinamento e teste.

    Args:
        X (np.ndarray): Matriz de características.
        y (np.ndarray): Rótulos.
        test_size (float): Proporção do conjunto de teste (0 a 1).
        random_state (int, optional): Semente para reprodutibilidade.

    Returns:
        tuple: (X_train, X_test, y_train, y_test)
    """
    if random_state is not None:
        np.random.seed(random_state)

    num_samples = X.shape[0]
    indices = np.arange(num_samples)
    np.random.shuffle(indices)

    split_idx = int(num_samples * (1 - test_size))
    train_indices = indices[:split_idx]
    test_indices = indices[split_idx:]

    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]

    return X_train, X_test, y_train, y_test