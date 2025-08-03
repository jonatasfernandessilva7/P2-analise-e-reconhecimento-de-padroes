import os
import sys

import joblib
import librosa
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from scipy.io import wavfile
from dotenv import load_dotenv

from service_microfone import gravar_audio_microfone, stop_recording_continuous
from source.service_extracao import extrair_features, SR

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

print("Diretório de modelos:", MODELS_DIR)
for filename in ["minmax_scaler.pkl", "pca_final.pkl", "mlp_final.pkl", "labels_map.pkl"]:
    path = os.path.join(MODELS_DIR, filename)
    print(f"Checando: {path} -> {'Existe' if os.path.exists(path) else 'Não encontrado'}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Carregando minmax_scaler...")
        app.state.scaler = joblib.load(os.path.join(MODELS_DIR, "minmax_scaler.pkl"))
        print("Carregando pca_params...")
        app.state.pca = joblib.load(os.path.join(MODELS_DIR, "pca_final.pkl"))
        print("Carregando mlp_params...")
        app.state.best_mlp = joblib.load(os.path.join(MODELS_DIR, "mlp_final.pkl"))
        print("Carregando labels_map...")
        app.state.CLASSES = joblib.load(os.path.join(MODELS_DIR, "labels_map.pkl"))
        print("Modelos de ML carregados com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar modelos de ML: {e}")
        raise RuntimeError(f"Modelos de ML não carregados. Erro interno do servidor. Detalhe: {e}")

    yield

async def processar_audio_para_ml(app: FastAPI, caminho_audio: str):
    """
    Função auxiliar para extrair características e passar pelo pipeline de ML.
    """
    try:
        # Carregar o áudio em mono
        y, sr = librosa.load(caminho_audio, sr=SR, mono=True)
        if y is None or len(y) == 0:
            raise HTTPException(status_code=400, detail="Áudio inválido ou vazio.")

        # Extrair features
        features = extrair_features(y)
        features = np.array(features).reshape(1, -1)

        # Normalização
        scaled = app.state.scaler.transform(features)

        # Redução de dimensionalidade com PCA
        reduced = app.state.pca.transform(scaled)

        # Classificação com MLP
        pred = app.state.best_mlp.predict(reduced)[0]

        # Obter o rótulo original
        label = app.state.CLASSES[pred]

        return label

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar áudio para ML: {e}")

async def receber_e_processar_audio(request:Request, file: UploadFile = File(...)):
    """
    Para uma gravação contínua em andamento, processa o áudio:
    - Lê o arquivo gerado
    - Extrai características e classifica usando o modelo MLP
    - Retorna as informações como JSON
    """
    # Para a gravação e pega o caminho do arquivo .wav
    try:
        caminho_temp = f"/tmp/{file.filename}"

        # Salva o arquivo enviado
        with open(caminho_temp, "wb") as f:
            f.write(await file.read())

        if os.path.getsize(caminho_temp) == 0:
            raise HTTPException(status_code=400, detail="Arquivo enviado está vazio.")

        # Lê o conteúdo do arquivo WAV
        rate, signal = wavfile.read(caminho_temp)

        # Se estéreo, pega só um canal
        if len(signal.shape) > 1:
            signal = signal[:, 0]

        detalhes_evento = {
            "caminho_audio": caminho_temp,
            "duracao_segundos": f"{len(signal) / rate:.2f}",
            "sample_rate": str(rate)
        }

        try:
            ml_prediction = await processar_audio_para_ml(request.app, caminho_temp)
            detalhes_evento["ml_prediction"] = ml_prediction
        except Exception as e:
            detalhes_evento["ml_error"] = f"Erro no modelo: {e}"

        return JSONResponse({
            "status": 200,
            "message": "success",
            "body": detalhes_evento
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao receber/processar áudio: {e}")
