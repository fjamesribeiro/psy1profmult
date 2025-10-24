from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import clientes, agendamentos, auth
from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Clientes e Agendamentos",
    description="API REST para gerenciamento de clientes e agendamentos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
app.include_router(agendamentos.router, prefix="/agendamentos", tags=["agendamentos"])

#main
@app.get("/")
def read_root():
    return {"message": "API funcionando", "docs": "/docs"}