DATASET_PATH = "Dataset-comandos-voz"

SR = 22050

FAIXAS_FREQUENCIA = [
    (150, 300),
    (300, 450),
    (450, 600),
    (600, 750),
    (750, 900),
    (900, 1050),
    (1050, 1200),
    (1200, 1350),
    (1350, 1500),
    (1500, 1650),
    (1650, 1800),
    (1800, 1950),
    (1950, 2100),
]

N_COMPONENTES_PCA = 0.99

CLASSES = [
    'Brincar', 'Comer', 'Corrida', 'Entrar',
    'Partida', 'Procurar', 'Sair', 'Testar'
]
