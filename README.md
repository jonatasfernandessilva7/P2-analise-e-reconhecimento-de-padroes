### Esta é uma aplicação desenvolvida para a prova 02 da disciplina de Aprendizado de Máquina e Reconhecimento de Padrões.

## A aplicação

A aplicação consiste em um sistema que recebe um áudio, enviado de duas maneiras:
1. Microfone local
2. Envio de um áudio gravado

A aplicação deve identificar e classificar corretamente o comando que foi dito.

## Comandos (palavras) a serem identificados e classificados

- Brincar
- Comer
- Corrida
- Entrar
- Partida
- Procurar
- Sair
- Testar

## Tecnologias
- Para o backend: python, por meio do fastAPI.
- Para o frontend: Ângular (v20)

## Técnicas utilizadas para a análise de padrões
- LPC
- MLP
- PCA
- Box Cox
- Transformada de Fourier

## Dataset

<a href="https://github.com/jonatasfernandessilva7/P2-analise-e-reconhecimento-de-padroes/blob/master/source/Dataset-comandos-voz-20250708T141849Z-1-001.zip">Audios</a>

## Pré requisitos

- Ter o python instalado: <a href="https://www.python.org/downloads/"><strong>Baixe Aqui</strong></a>

## Passo a Passo Como executar

1. Clone o repo: 
```bash 
 git clone https://github.com/jonatasfernandessilva7/P2-analise-e-reconhecimento-de-padroes.git
```

2. Instale as bibliotecas:
```bash
pip install requirements.txt
```

3. Rode primeiro o servidor:
```bash
fastapi dev server.py
```

4. Com o servidor rodando execute o frontend:
```bash
ng serve
```