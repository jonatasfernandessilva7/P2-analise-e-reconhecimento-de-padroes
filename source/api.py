import os
import sys

from fastapi.responses import JSONResponse
from fastapi import APIRouter, File, UploadFile, HTTPException
from controller_audio import iniciarGravacao, receber_e_processar_audio, processar_audio_enviado

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

router = APIRouter(
    prefix="/v1"
)

@router.post("/enviar-audio-wav")
async def enviar_audio_wav(file: UploadFile = File(...)):
    try:
        return await processar_audio_enviado(file)
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload e processar áudio: {e}")

@router.post("/iniciar-gravacao")
async def receber_audio():
    try:
        # A função iniciarGravacao() já deve lidar com a lógica de iniciar a gravação
        # e talvez retornar um status ou ID de gravação se necessário.
        # Por simplicidade aqui, apenas chamamos e confirmamos o início.
        await iniciarGravacao()  # Assumimos que iniciarGravacao() é assíncrona ou não bloqueia
        return JSONResponse({"status": 200, "message": "Gravação iniciada com sucesso."})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar gravação: {e}")


@router.post("/parar-gravacao")
async def parar_gravacao():
    try:
        return await receber_e_processar_audio()
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar e processar gravação: {e}")