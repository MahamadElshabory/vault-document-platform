from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router

from app.core.metrics import metrics_app

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Vault API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/metrics", metrics_app)

app.include_router(auth_router)
app.include_router(documents_router)

