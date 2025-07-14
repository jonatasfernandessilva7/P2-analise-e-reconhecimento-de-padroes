def pca_fit_transform(X, n_components):
    """
    Ajusta o PCA e transforma os dados, retornando os dados reduzidos
    e os componentes principais e a média para transformações futuras.

    Args:
        X (np.ndarray): Matriz de características (n_amostras, n_caracteristicas).
        n_components (int or float): Número de componentes a manter ou
                                     fração da variância a explicar (0 a 1).

    Returns:
        tuple: (reduced_data, pca_params) onde:
            reduced_data (np.ndarray): Dados com dimensionalidade reduzida.
            pca_params (dict): Dicionário contendo 'components' e 'mean' do PCA.
    """
    # 1. Centralizar os dados
    data_mean = np.mean(X, axis=0)
    X_centered = X - data_mean

    # 2. Calcular a matriz de covariância
    # np.cov espera que cada coluna seja uma observação e cada linha uma variável
    covariance_matrix = np.cov(X_centered, rowvar=False)

    # 3. Calcular os autovalores e autovetores
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

    # Autovetores são retornados como colunas; precisamos transpor para que cada linha seja um autovetor
    eigenvectors = eigenvectors.T

    # 4. Ordenar os autovetores pelos seus autovalores correspondentes em ordem decrescente
    sorted_indices = np.argsort(eigenvalues)[::-1]
    sorted_eigenvalues = eigenvalues[sorted_indices]
    sorted_eigenvectors = eigenvectors[sorted_indices]

    # 5. Selecionar os principais componentes
    if 0 < n_components < 1:
        cumulative_variance_ratio = np.cumsum(sorted_eigenvalues) / np.sum(sorted_eigenvalues)
        num_components_to_keep = np.where(cumulative_variance_ratio >= n_components)[0][0] + 1
    else:
        num_components_to_keep = int(n_components)

    components = sorted_eigenvectors[:num_components_to_keep]

    # 6. Projetar os dados
    reduced_data = np.dot(X_centered, components.T)

    pca_params = {
        'components': components,
        'mean': data_mean
    }

    return reduced_data, pca_params


def pca_transform(X, pca_params):
    """
    Transforma novos dados usando os parâmetros ajustados do PCA.

    Args:
        X (np.ndarray): Matriz de novas características.
        pca_params (dict): Dicionário de parâmetros de ajuste retornado por pca_fit_transform.

    Returns:
        np.ndarray: Dados com dimensionalidade reduzida.
    """
    components = pca_params['components']
    data_mean = pca_params['mean']

    # Centralizar os novos dados usando a média do treinamento
    X_centered = X - data_mean

    # Projetar os dados
    reduced_data = np.dot(X_centered, components.T)
    return reduced_data


import numpy as np


# Funções de ativação
def relu(x):
    return np.maximum(0, x)


def relu_derivative(x):
    return (x > 0).astype(float)


def softmax(x):
    exp_scores = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_scores / np.sum(exp_scores, axis=1, keepdims=True)


# Função de perda
def cross_entropy_loss(predictions, targets_one_hot):
    predictions = np.clip(predictions, 1e-12, 1 - 1e-12)
    return -np.sum(targets_one_hot * np.log(predictions)) / len(predictions)
