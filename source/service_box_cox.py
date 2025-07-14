_boxcox_lambda_val = 0  # Valor padrão para lambda (logaritmo)
_boxcox_offset = 1e-7  # Pequeno valor para garantir que os dados sejam positivos

def boxcox_fit_transform(X, lambda_val=_boxcox_lambda_val, offset=_boxcox_offset):
    """
    Ajusta e transforma os dados usando a transformação Box-Cox simplificada,
    e padroniza os dados resultantes (média 0, desvio padrão 1).

    Args:
        X (np.ndarray): Matriz de características (n_amostras, n_caracteristicas).
        lambda_val (float): O parâmetro lambda para a transformação Box-Cox.
        offset (float): Um pequeno valor para garantir que os dados sejam positivos.

    Returns:
        tuple: (transformed_X, fitted_params) onde:
            transformed_X (np.ndarray): Dados transformados e padronizados.
            fitted_params (dict): Dicionário contendo 'mean' e 'std' para padronização.
    """
    X_positive = X + offset

    if lambda_val == 0:
        transformed_X = np.log(X_positive)
    else:
        transformed_X = (X_positive ** lambda_val - 1) / lambda_val

    # Padronização
    feature_means = np.mean(transformed_X, axis=0)
    feature_stds = np.std(transformed_X, axis=0)
    # Evitar divisão por zero para características com desvio padrão zero
    feature_stds[feature_stds == 0] = 1.0

    transformed_X = (transformed_X - feature_means) / feature_stds

    fitted_params = {
        'lambda_val': lambda_val,
        'offset': offset,
        'mean': feature_means,
        'std': feature_stds
    }

    return transformed_X, fitted_params


def boxcox_transform(X, fitted_params):
    """
    Transforma novos dados usando os parâmetros ajustados da transformação Box-Cox.

    Args:
        X (np.ndarray): Matriz de novas características.
        fitted_params (dict): Dicionário de parâmetros de ajuste retornado por boxcox_fit_transform.

    Returns:
        np.ndarray: Dados transformados e padronizados.
    """
    lambda_val = fitted_params['lambda_val']
    offset = fitted_params['offset']
    feature_means = fitted_params['mean']
    feature_stds = fitted_params['std']

    X_positive = X + offset

    if lambda_val == 0:
        transformed_X = np.log(X_positive)
    else:
        transformed_X = (X_positive ** lambda_val - 1) / lambda_val

    transformed_X = (transformed_X - feature_means) / feature_stds

    return transformed_X
