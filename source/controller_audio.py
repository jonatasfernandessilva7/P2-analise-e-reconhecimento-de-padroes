import datetime
import os
import sys

import joblib
import numpy as np

'''
Fluxo

recebe audio -> extrai as features via FFT -> transforma os dados via box cox e PCA -> classifica no MLP 

'''

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from scipy.io import wavfile
from dotenv import load_dotenv

from source.service_box_cox import boxcox_transform
from source.service_mlp import mlp_predict_proba
from source.service_pca import pca_transform
from service_fft import fft_analysis_service, filtro_passa_baixa, detectar_padroes, salvar_espectrograma
from service_microfone import gravar_audio_microfone, stop_recording_continuous

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

print("Diretório de modelos:", MODELS_DIR)
for filename in ["boxcox_params.pkl", "pca_params.pkl", "mlp_params.pkl", "labels_map.pkl"]:
    path = os.path.join(MODELS_DIR, filename)
    print(f"Checando: {path} -> {'Existe' if os.path.exists(path) else 'Não encontrado'}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Carregando boxcox_params...")
        app.state.boxcox_params = joblib.load(os.path.join(MODELS_DIR, "boxcox_params.pkl"))
        print("Carregando pca_params...")
        app.state.pca_params = joblib.load(os.path.join(MODELS_DIR, "pca_params.pkl"))
        print("Carregando mlp_params...")
        app.state.mlp_params = joblib.load(os.path.join(MODELS_DIR, "mlp_params.pkl"))
        print("Carregando labels_map...")
        app.state.labels_map = joblib.load(os.path.join(MODELS_DIR, "labels_map.pkl"))
        app.state.inverse_labels_map = {v: k for k, v in app.state.labels_map.items()}
        print("Modelos de ML carregados com sucesso!")
    except Exception as e:
        print(f"Erro ao carregar modelos de ML: {e}")
        raise RuntimeError(f"Modelos de ML não carregados. Erro interno do servidor. Detalhe: {e}")

    yield

async def processar_audio_para_ml(app: FastAPI,caminho_audio: str):
    """
    Função auxiliar para extrair características e passar pelo pipeline de ML.
    """

    state = app.state

    if not hasattr(state, "mlp_params"):
        raise HTTPException(status_code=500, detail="Modelos de ML não carregados.")

    # 1. Extração de características (usando service_fft)
    features_dict = fft_analysis_service(caminho_audio)
    if "erro" in features_dict:
        raise HTTPException(status_code=500, detail=f"Erro na extração de features: {features_dict['erro']}")

    # Coleta as características em uma lista ordenada (deve ser a mesma ordem do treinamento)
    feature_vector = np.array([[
        features_dict['pico_frequencia'],
        features_dict['pico_amplitude'],
        features_dict['energia_total'],
        features_dict['media_abs'],
        features_dict['centroide_espectral'],
        features_dict['largura_banda_espectral'],
        features_dict['zcr']
    ]])

    transformed_features = boxcox_transform(feature_vector, state.boxcox_params)
    reduced_features = pca_transform(transformed_features, state.pca_params)
    probabilities = mlp_predict_proba(reduced_features, state.mlp_params)
    predicted_class_index = np.argmax(probabilities, axis=1)[0]
    predicted_class_name = state.inverse_labels_map.get(predicted_class_index, "Classe Desconhecida")

    # Você pode retornar as probabilidades ou apenas a classe prevista
    return {
        "predicted_class_name": predicted_class_name,
        "prediction_probabilities": probabilities[0].tolist()  # Converter para lista para JSON
    }


async def iniciarGravacao():
    """
    Inicia a gravação de áudio do microfone.
    Retorna o caminho do arquivo de áudio temporário onde a gravação será salva.
    """
    gravacao = gravar_audio_microfone()
    if gravacao is None:
        raise HTTPException(status_code=404, detail="Arquivo de áudio é nulo ou a gravação falhou.")
    return gravacao


async def receber_e_processar_audio(request:Request):
    """
    Para uma gravação contínua em andamento, processa o arquivo de áudio.
    Realiza análise de Fourier, filtragem, detecção de padrões, salvamento de espectrograma
    e reconhecimento de fala.
    """
    # stop_recording_continuous() deve retornar o caminho do arquivo gravado ou uma mensagem de erro
    caminho_temp = stop_recording_continuous()

    if "Nenhuma gravação" in caminho_temp or "Erro" in caminho_temp:
        raise HTTPException(status_code=400, detail=caminho_temp)

    try:
        # Verifica se o arquivo existe e não está vazio
        if not os.path.exists(caminho_temp) or os.path.getsize(caminho_temp) == 0:
            raise HTTPException(status_code=500, detail="Arquivo de áudio gerado está vazio ou não existe.")

        # Lê o arquivo WAV
        rate, signal = wavfile.read(caminho_temp)

        # Converte para mono se for estéreo
        if len(signal.shape) > 1:
            signal = signal[:, 0]

        # Analisa o som usando Fourier
        resultado_analise_fft = fft_analysis_service(caminho_temp)

        detalhes_evento = {
            "caminho_audio": caminho_temp,
            "duracao_segundos": str(len(signal) / rate),
            "sample_rate": str(rate)
        }

        if "pico_frequencia" in resultado_analise_fft:
            detalhes_evento.update({k: str(v) for k, v in resultado_analise_fft.items() if k != "status"})
        elif "erro" in resultado_analise_fft:
            detalhes_evento["erro_analise_som"] = resultado_analise_fft["erro"]

        # Aplica filtro passa-baixa e detecta padrões
        signal_filtrado = filtro_passa_baixa(signal, rate)
        padrao = detectar_padroes(signal_filtrado, rate)

        # Salva espectrograma
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        espectrograma_path = salvar_espectrograma(signal, rate, timestamp)

        detalhes_evento["padrao_detectado"] = padrao
        detalhes_evento["espectrograma_path"] = espectrograma_path

        try:
            ml_results = await processar_audio_para_ml(request.app, caminho_temp)
            detalhes_evento["ml_prediction"] = ml_results
        except HTTPException as ml_http_exc:
            detalhes_evento["ml_error"] = str(ml_http_exc.detail)
        except Exception as ml_exc:
            detalhes_evento["ml_error"] = f"Erro na análise de ML: {ml_exc}"

        return JSONResponse({"status": 200, "message": "success", "body": detalhes_evento})

    except FileNotFoundError:
        raise HTTPException(status_code=404,
                            detail="Arquivo de áudio não encontrado após gravação. Verifique se o processo de gravação salvou o arquivo corretamente.")
    except Exception as e:
        print(f"Erro inesperado em receber_e_processar_audio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro durante o processamento do áudio: {e}")


async def processar_audio_enviado(request:Request, file: UploadFile = File(...)):
    """
    Recebe um arquivo de áudio WAV enviado via upload, processa-o
    e retorna uma análise detalhada.
    """
    try:
        # Validação do formato do arquivo
        if not file.filename.endswith(".wav"):
            raise HTTPException(status_code=400, detail="O arquivo deve estar no formato WAV.")

        # Cria um diretório temporário para uploads se não existir
        pasta_temp = os.path.join(os.path.dirname(__file__), "..",
                                  "audios_uploads")  # Use uma pasta diferente para uploads
        os.makedirs(pasta_temp, exist_ok=True)

        # Gera um nome de arquivo único com timestamp
        caminho_temp = os.path.join(pasta_temp,
                                    f"upload_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")

        contents = await file.read()
        with open(caminho_temp, "wb") as f:
            f.write(contents)

        # Lê o arquivo WAV salvo
        rate, signal = wavfile.read(caminho_temp)
        if len(signal.shape) > 1:
            signal = signal[:, 0]

        # Analisa o som usando Fourier
        resultado_analise_fft = fft_analysis_service(caminho_temp)

        detalhes_evento = {
            "caminho_audio": caminho_temp,
            "duracao_segundos": str(len(signal) / rate),
            "sample_rate": str(rate)
        }

        if "pico_frequencia" in resultado_analise_fft:
            detalhes_evento.update({k: str(v) for k, v in resultado_analise_fft.items() if k != "status"})
        elif "erro" in resultado_analise_fft:
            detalhes_evento["erro_analise_som"] = resultado_analise_fft["erro"]

        # Aplica filtro passa-baixa e detecta padrões
        signal_filtrado = filtro_passa_baixa(signal, rate)
        padrao = detectar_padroes(signal_filtrado, rate)

        # Salva espectrograma
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        espectrograma_path = salvar_espectrograma(signal, rate, timestamp)

        detalhes_evento["padrao_detectado"] = padrao
        detalhes_evento["espectrograma_path"] = espectrograma_path

        try:
            ml_results = await processar_audio_para_ml(request.app, caminho_temp)
            detalhes_evento["ml_prediction"] = ml_results
        except HTTPException as ml_http_exc:
            detalhes_evento["ml_error"] = str(ml_http_exc.detail)
        except Exception as ml_exc:
            detalhes_evento["ml_error"] = f"Erro na análise de ML: {ml_exc}"

        return JSONResponse({"status": 200, "message": "success", "body": detalhes_evento})

    except Exception as e:
        print(f"Erro inesperado em processar_audio_enviado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar o áudio enviado: {e}")