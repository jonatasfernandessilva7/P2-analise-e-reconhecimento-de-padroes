from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api

app = FastAPI(title="P2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)