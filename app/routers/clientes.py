from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
import schemas
from database import get_db
from services.cliente_service import ClienteService

router = APIRouter()

@router.post("/", response_model=schemas.Cliente, status_code=status.HTTP_201_CREATED)
def create_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    return ClienteService.create_cliente(db, cliente)

@router.get("/", response_model=List[schemas.Cliente])
def read_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return ClienteService.get_clientes(db, skip, limit)

@router.get("/{cliente_id}", response_model=schemas.Cliente)
def read_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return ClienteService.get_cliente_by_id(db, cliente_id)

@router.get("/email/{email}", response_model=schemas.Cliente)
def read_cliente_by_email(email: str, db: Session = Depends(get_db)):
    return ClienteService.get_cliente_by_email(db, email)

@router.put("/{cliente_id}", response_model=schemas.Cliente)
def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    return ClienteService.update_cliente(db, cliente_id, cliente)

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    ClienteService.delete_cliente(db, cliente_id)