import sys
import zipfile
import os
import numpy as np

# Adiciona o diretório acima ao path para importar os módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from source.service_preparacao_dados import load_and_extract_features, train_test_split_custom
from source.service_mlp import initialize_mlp_parameters, mlp_predict, mlp_train
from source.service_pca import pca_fit_transform, pca_transform
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.utils.multiclass import unique_labels

# === 1. Extração do dataset ===
with zipfile.ZipFile('Dataset-comandos-voz-20250708T141849Z-1-001.zip', 'r') as zip_ref:
    zip_ref.extractall('dataset')

root_path_audios = "./dataset"
subdirs_audios = [i for i in os.listdir(root_path_audios) if os.path.isdir(os.path.join(root_path_audios, i))]

if len(subdirs_audios) == 1:
    audios_dir = os.path.join(root_path_audios, subdirs_audios[0])
else:
    raise Exception("Estrutura do dataset inesperada. Verifique o conteúdo do ZIP.")

# === 2. Mapeamento das classes ===
labels_map = {
    "Brincar": 0,
    "Comer" : 1,
    "Corrida": 2,
    "Entrar": 3,
    "Partida": 4,
    "Procurar": 5,
    "Sair": 6,
    "Testar": 7
}

# === 3. Carregar os dados ===
X, y = load_and_extract_features(audios_dir, labels_map)

print(f"número de amostras: {len(y)}\nAtributos por amostra: {X.shape[1]}")

# número de amostras por classe
for classe, idx in labels_map.items():
    count = np.sum(y == idx)
    print(f"Classe '{classe}' — {count} amostras")

# === 4. Divisão treino/teste ===
X_train, X_test, y_train, y_test = train_test_split_custom(X, y, test_size=0.2, random_state=42)

# === 5. Aplicar PCA ===
X_train_pca, pca_params = pca_fit_transform(X_train, n_components=0.95)
X_test_pca = pca_transform(X_test, pca_params)

# === 6. Treinar MLP ===
input_size = X_train_pca.shape[1]
hidden_size = 28
output_size = len(labels_map)

params = initialize_mlp_parameters(input_size, hidden_size, output_size)
params = mlp_train(X_train_pca, y_train, params, learning_rate=0.01, epochs=300)

# === 7. Predição e avaliação ===
y_pred = mlp_predict(X_test_pca, params)
acc = accuracy_score(y_test, y_pred)

print("\nAcurácia:", round(acc * 100, 2), "%")

# === 8. Relatório de classificação ===
labels_presentes = sorted(unique_labels(y_test, y_pred))
target_names_presentes = [classe for classe, idx in labels_map.items() if idx in labels_presentes]

print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred, labels=labels_presentes, target_names=target_names_presentes))

print("\nMatriz de Confusão:")
print(confusion_matrix(y_test, y_pred, labels=labels_presentes))
