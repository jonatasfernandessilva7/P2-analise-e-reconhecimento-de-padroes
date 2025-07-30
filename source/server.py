from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api
from source.controller_audio import lifespan

app = FastAPI(title="P2", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#injetect for render
@app.get("/v1/")
async def read_root():
    return {"message": "Service is running!"}

app.include_router(api.router)
