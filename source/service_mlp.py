def initialize_mlp_parameters(input_size, hidden_size, output_size):
    """
    Inicializa os pesos e vieses da rede MLP.

    Args:
        input_size (int): Número de características de entrada.
        hidden_size (int): Número de neurônios na camada oculta.
        output_size (int): Número de classes de saída.

    Returns:
        dict: Um dicionário contendo os pesos e vieses da rede.
    """
    params = {
        'W1': np.random.randn(input_size, hidden_size) * 0.01,  # Pesos input -> hidden
        'b1': np.zeros((1, hidden_size)),  # Vieses hidden
        'W2': np.random.randn(hidden_size, output_size) * 0.01,  # Pesos hidden -> output
        'b2': np.zeros((1, output_size))  # Vieses output
    }
    return params


def mlp_train(X, y, params, learning_rate=0.01, epochs=1000):
    """
    Treina o modelo MLP usando propagação feedforward e retropropagação.

    Args:
        X (np.ndarray): Matriz de características de treinamento.
        y (np.ndarray): Rótulos de treinamento (codificados numericamente, e.g., 0, 1, 2).
        params (dict): Dicionário de pesos e vieses do MLP.
        learning_rate (float): Taxa de aprendizado.
        epochs (int): Número de épocas de treinamento.

    Returns:
        dict: O dicionário de pesos e vieses atualizado após o treinamento.
    """
    num_samples = X.shape[0]
    output_size = params['W2'].shape[1]

    # Converter y para one-hot encoding
    y_one_hot = np.zeros((num_samples, output_size))
    y_one_hot[np.arange(num_samples), y] = 1

    for epoch in range(epochs):
        # Propagação Feedforward
        # Camada de entrada para oculta
        hidden_layer_input = np.dot(X, params['W1']) + params['b1']
        hidden_layer_output = relu(hidden_layer_input)

        # Camada oculta para saída
        output_layer_input = np.dot(hidden_layer_output, params['W2']) + params['b2']
        predictions = softmax(output_layer_input)

        # Cálculo do erro (derivada da perda em relação à saída)
        error_output = predictions - y_one_hot

        # Retropropagação
        # Gradientes para pesos e vieses da camada oculta para saída
        dW2 = np.dot(hidden_layer_output.T, error_output)
        db2 = np.sum(error_output, axis=0, keepdims=True)

        # Erro na camada oculta
        error_hidden = np.dot(error_output, params['W2'].T) * relu_derivative(hidden_layer_input)

        # Gradientes para pesos e vieses da camada de entrada para oculta
        dW1 = np.dot(X.T, error_hidden)
        db1 = np.sum(error_hidden, axis=0, keepdims=True)

        # Atualização dos pesos e vieses
        params['W1'] -= learning_rate * dW1
        params['b1'] -= learning_rate * db1
        params['W2'] -= learning_rate * dW2
        params['b2'] -= learning_rate * db2

        if epoch % 100 == 0:
            loss = cross_entropy_loss(predictions, y_one_hot)
            print(f"Época {epoch}, Perda: {loss:.4f}")

    return params


def mlp_predict_proba(X, params):
    """
    Realiza a propagação feedforward para obter as probabilidades de classe.

    Args:
        X (np.ndarray): Matriz de características para previsão.
        params (dict): Dicionário de pesos e vieses do MLP.

    Returns:
        np.ndarray: Probabilidades para cada classe.
    """
    hidden_layer_input = np.dot(X, params['W1']) + params['b1']
    hidden_layer_output = relu(hidden_layer_input)
    output_layer_input = np.dot(hidden_layer_output, params['W2']) + params['b2']
    predictions = softmax(output_layer_input)
    return predictions


def mlp_predict(X, params):
    """
    Realiza a previsão de classe para novos dados.

    Args:
        X (np.ndarray): Matriz de características para previsão.
        params (dict): Dicionário de pesos e vieses do MLP.

    Returns:
        np.ndarray: Array de rótulos de classe previstos.
    """
    probabilities = mlp_predict_proba(X, params)
    return np.argmax(probabilities, axis=1)