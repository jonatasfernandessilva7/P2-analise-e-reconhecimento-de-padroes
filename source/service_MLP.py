import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay, classification_report
import matplotlib.pyplot as plt
from config import N_COMPONENTES_PCA, CLASSES
import joblib

X = np.load("features/X_fft_aug.npy")
y = np.load("features/y_labels_aug.npy")

scaler = MinMaxScaler(feature_range=(0,1))
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=N_COMPONENTES_PCA)
X_pca = pca.fit_transform(X_scaled)

X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, stratify=y, random_state=42)

param_grid = {
    'hidden_layer_sizes': [
        (30,), (40,), (20, 10),
        (40, 20), (30, 15, 5), (30,20), (30,40), (30,10), (30,30)
    ],
    'learning_rate_init': [0.01, 0.1, 0.5, 0.001, 0.005, 0.05],
    'alpha': [0.0001, 0.001, 0.01, 0.1],
    'max_iter': [1000, 2000, 3000],
    'solver': ['adam'],
    'activation': ['relu'],
    'early_stopping': [True],
    'validation_fraction': [0.2]
}

grid = GridSearchCV(MLPClassifier(random_state=42),
                    param_grid,
                    scoring='accuracy',
                    cv=5,
                    n_jobs=-1,
                    verbose=1)

print(" Buscando melhores hiperparâmetros...")
grid.fit(X_train, y_train)

print("\n Melhor configuração encontrada:")
print(grid.best_params_)
print(f"Acurácia média (CV): {grid.best_score_ * 100:.2f}%")

best_mlp = grid.best_estimator_


joblib.dump(CLASSES, "models/labels_map.pkl")
joblib.dump(best_mlp, "models/mlp_final.pkl")
joblib.dump(pca, "models/pca_final.pkl")
joblib.dump(scaler, "models/minmax_scaler.pkl")
print("modelos salvos na pasta /models")

print("\n Plotando curva de aprendizado do melhor modelo...")

X_train, X_val, y_train, y_val = train_test_split(X_pca, y, test_size=0.2, stratify=y, random_state=42)

mlp = MLPClassifier(
    hidden_layer_sizes=best_mlp.hidden_layer_sizes,
    activation=best_mlp.activation,
    learning_rate_init=best_mlp.learning_rate_init,
    alpha=best_mlp.alpha,
    solver=best_mlp.solver,
    max_iter=1,
    warm_start=True,
    random_state=42
)

train_scores = []
val_scores = []
n_epochs = 100

for epoch in range(n_epochs):
    mlp.fit(X_train, y_train)
    train_scores.append(accuracy_score(y_train, mlp.predict(X_train)))
    val_scores.append(accuracy_score(y_val, mlp.predict(X_val)))

y_pred_final = mlp.predict(X_val)

print("\n Classification Report:")
print(classification_report(y_val, y_pred_final, target_names=CLASSES))

plt.figure(figsize=(8, 5))
plt.plot(train_scores, label="Treino")
plt.plot(val_scores, label="Validação")
plt.title("Curva de Acurácia por Época (MLP Otimizado)")
plt.xlabel("Época")
plt.ylabel("Acurácia")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print("\n Matriz de confusão com o melhor modelo...")
y_pred_final = mlp.predict(X_val)
cm = confusion_matrix(y_val, y_pred_final)

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASSES)
disp.plot(cmap="Blues", xticks_rotation=45)
plt.title("Matriz de Confusão - MLP Otimizado")
plt.tight_layout()
plt.show()
