from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router


app = FastAPI(
    title="Vault API"
)


app.include_router(auth_router)
app.include_router(documents_router)