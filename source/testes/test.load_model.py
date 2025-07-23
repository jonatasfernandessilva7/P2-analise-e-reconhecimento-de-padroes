import joblib
from pathlib import Path

# Caminho absoluto para a pasta "models"
BASE_DIR = Path(__file__).resolve().parent.parent  # Vai de /testes para /source
MODELS_DIR = BASE_DIR / "models"

print(f"MODELS_DIR: {MODELS_DIR}")

for name in ["boxcox_params", "pca_params", "mlp_params", "labels_map"]:
    path = MODELS_DIR / f"{name}.pkl"
    try:
        print(f"Carregando {name}...")
        obj = joblib.load(path)
        print(f"{name} carregado com sucesso! Tipo: {type(obj)}")
    except Exception as e:
        print(f"Erro ao carregar {name}: {e}")
