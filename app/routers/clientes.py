from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas
from app.services.cliente_service import ClienteService
from app.services.auth import get_current_profissional

router = APIRouter()

# Dependency para obter o profissional_id
def get_profissional_id(current_user = Depends(get_current_profissional)) -> int:
    return current_user.profissional_id

@router.post("/", response_model=schemas.Cliente, status_code=status.HTTP_201_CREATED)
async def create_cliente(cliente: schemas.ClienteCreate, profissional_id: int = Depends(get_profissional_id)):
    return ClienteService.create_cliente(db, cliente)

@router.get("/", response_model=List[schemas.Cliente])
async def read_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_profissional_id)):
    return ClienteService.get_clientes(db, skip, limit)

@router.get("/{cliente_id}", response_model=schemas.Cliente)
async def read_cliente(cliente_id: int, db: Session = Depends(get_profissional_id)):
    return ClienteService.get_cliente_by_id(db, cliente_id)

@router.get("/email/{email}", response_model=schemas.Cliente)
async def read_cliente_by_email(email: str, db: Session = Depends(get_profissional_id)):
    return ClienteService.get_cliente_by_email(db, email)

@router.put("/{cliente_id}", response_model=schemas.Cliente)
async def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_profissional_id)):
    return ClienteService.update_cliente(db, cliente_id, cliente)

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cliente(cliente_id: int, db: Session = Depends(get_profissional_id)):
    ClienteService.delete_cliente(db, cliente_id)