import os
import sys
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, Request
from controller_audio import iniciarGravacao, receber_e_processar_audio

router = APIRouter(
    prefix="/v1"
)

@router.post("/iniciar-gravacao")
async def receber_audio():
    try:
        request_idempotency_key = str(uuid.uuid4())
        await iniciarGravacao(idempotency_key=request_idempotency_key)
        return JSONResponse({"status": 200, "message": "Gravação iniciada com sucesso."})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar gravação: {e}")


@router.post("/parar-gravacao")
async def parar_gravacao(request:Request):
    try:
        return await receber_e_processar_audio(request)
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar e processar gravação: {e}")