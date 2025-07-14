import datetime
import os
import sys
import numpy as np

# Ensure the parent directory is in the sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from scipy.io import wavfile  # Used for reading .wav files
from dotenv import load_dotenv

# Import your service functions
# Make sure 'service_fft.py' and 'service_microfone.py' are correctly
# located relative to your sys.path or directly in your project.
from service_fft import analisar_som_fourier, filtro_passa_baixa, detectar_padroes, salvar_espectrograma
from service_microfone import gravar_audio_microfone, reconhecer_fala, stop_recording_continuous

# Load environment variables (e.g., for API keys, if 'reconhecer_fala' uses one)
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Sistema de Análise de Áudio",
    description="API para gravar, processar e analisar áudio, detectando padrões e transcrevendo fala.",
    version="1.0.0"
)


# --- Funções de Serviço de Áudio (as que você já forneceu) ---
# Você as moveria para um módulo separado (e.g., 'controllers/audio_controller.py')
# ou as manteria aqui se este for o arquivo principal do controlador.

async def iniciarGravacao():
    """
    Inicia a gravação de áudio do microfone.
    Retorna o caminho do arquivo de áudio temporário onde a gravação será salva.
    """
    gravacao = gravar_audio_microfone()
    if gravacao is None:
        raise HTTPException(status_code=404, detail="Arquivo de áudio é nulo ou a gravação falhou.")
    return gravacao  # Retorna o caminho do arquivo de gravação


async def receber_e_processar_audio():
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

        # Analisa o som usando Fourier (do seu 'service_analise_som')
        resultado_analise = analisar_som_fourier(caminho_temp)

        detalhes_evento = {
            "caminho_audio": caminho_temp,
            "duracao_segundos": str(len(signal) / rate),
            "sample_rate": str(rate)
        }

        # Adiciona resultados da análise de Fourier ao dicionário
        if "pico_frequencia" in resultado_analise and "pico_amplitude" in resultado_analise:
            detalhes_evento["pico_frequencia"] = str(resultado_analise["pico_frequencia"])
            detalhes_evento["pico_amplitude"] = str(resultado_analise["pico_amplitude"])
            detalhes_evento["energia_total"] = str(resultado_analise.get("energia_total"))  # Add new features
            detalhes_evento["media_abs"] = str(resultado_analise.get("media_abs"))
            detalhes_evento["centroide_espectral"] = str(resultado_analise.get("centroide_espectral"))
            detalhes_evento["largura_banda_espectral"] = str(resultado_analise.get("largura_banda_espectral"))
            detalhes_evento["zcr"] = str(resultado_analise.get("zcr"))
            detalhes_evento["status_analise_som"] = resultado_analise.get("status", "desconhecido")
        elif "erro" in resultado_analise:
            detalhes_evento["erro_analise_som"] = resultado_analise["erro"]

        # Aplica filtro passa-baixa e detecta padrões
        signal_filtrado = filtro_passa_baixa(signal, rate)
        padrao = detectar_padroes(signal_filtrado, rate)

        # Salva espectrograma
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        espectrograma_path = salvar_espectrograma(signal, rate, timestamp)

        detalhes_evento["padrao_detectado"] = padrao
        detalhes_evento["espectrograma_path"] = espectrograma_path

        # Realiza reconhecimento de fala
        texto_falado = reconhecer_fala(caminho_temp)
        print(f"Texto reconhecido: {texto_falado}")
        detalhes_evento["texto_falado"] = texto_falado

        return JSONResponse({"status": 200, "message": "success", "body": detalhes_evento})

    except FileNotFoundError:
        raise HTTPException(status_code=404,
                            detail="Arquivo de áudio não encontrado após gravação. Verifique se o processo de gravação salvou o arquivo corretamente.")
    except Exception as e:
        print(f"Erro inesperado em receber_e_processar_audio: {e}")
        raise HTTPException(status_code=500, detail=f"Erro durante o processamento do áudio: {e}")


async def processar_audio_enviado(file: UploadFile = File(...)):
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

        # Salva o arquivo enviado
        contents = await file.read()
        with open(caminho_temp, "wb") as f:
            f.write(contents)

        # Lê o arquivo WAV salvo
        rate, signal = wavfile.read(caminho_temp)
        if len(signal.shape) > 1:
            signal = signal[:, 0]

        # Analisa o som usando Fourier
        resultado_analise = analisar_som_fourier(caminho_temp)

        detalhes_evento = {
            "caminho_audio": caminho_temp,
            "duracao_segundos": str(len(signal) / rate),
            "sample_rate": str(rate)
        }

        # Adiciona resultados da análise de Fourier ao dicionário
        if "pico_frequencia" in resultado_analise and "pico_amplitude" in resultado_analise:
            detalhes_evento["pico_frequencia"] = str(resultado_analise["pico_frequencia"])
            detalhes_evento["pico_amplitude"] = str(resultado_analise["pico_amplitude"])
            detalhes_evento["energia_total"] = str(resultado_analise.get("energia_total"))  # Add new features
            detalhes_evento["media_abs"] = str(resultado_analise.get("media_abs"))
            detalhes_evento["centroide_espectral"] = str(resultado_analise.get("centroide_espectral"))
            detalhes_evento["largura_banda_espectral"] = str(resultado_analise.get("largura_banda_espectral"))
            detalhes_evento["zcr"] = str(resultado_analise.get("zcr"))
            detalhes_evento["status_analise_som"] = resultado_analise.get("status", "desconhecido")
        elif "erro" in resultado_analise:
            detalhes_evento["erro_analise_som"] = resultado_analise["erro"]

        # Aplica filtro passa-baixa e detecta padrões
        signal_filtrado = filtro_passa_baixa(signal, rate)
        padrao = detectar_padroes(signal_filtrado, rate)

        # Salva espectrograma
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        espectrograma_path = salvar_espectrograma(signal, rate, timestamp)

        detalhes_evento["padrao_detectado"] = padrao
        detalhes_evento["espectrograma_path"] = espectrograma_path

        # Realiza reconhecimento de fala
        texto_falado = reconhecer_fala(caminho_temp)
        print(f"Texto reconhecido: {texto_falado}")
        detalhes_evento["texto_falado"] = texto_falado

        return JSONResponse({"status": 200, "message": "success", "body": detalhes_evento})

    except Exception as e:
        print(f"Erro inesperado em processar_audio_enviado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar o áudio enviado: {e}")