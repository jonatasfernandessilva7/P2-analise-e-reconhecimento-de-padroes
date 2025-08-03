import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from controller_audio import receber_e_processar_audio

router = APIRouter(
    prefix="/v1"
)

#injetect for render
@router.get("/")
async def read_root():
    return {"message": "Service is running!"}


@router.post("/upload-audio")
async def audio_upload_e_processamento(request:Request, file: UploadFile = File(...)):
    try:
        return await receber_e_processar_audio(request, file)
    except HTTPException as e:
        raise e  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao parar e processar gravação: {e}")
