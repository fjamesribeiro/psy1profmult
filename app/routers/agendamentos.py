from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas
from app.database import get_db
from app.services.agendamento_service import AgendamentoService

router = APIRouter()

@router.post("/", response_model=schemas.Agendamento, status_code=status.HTTP_201_CREATED)
def create_agendamento(agendamento: schemas.AgendamentoCreate, db: Session = Depends(get_db)):
    return AgendamentoService.create_agendamento(db, agendamento)

@router.get("/", response_model=List[schemas.Agendamento])
def read_agendamentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AgendamentoService.get_agendamentos(db, skip, limit)

@router.get("/{agendamento_id}", response_model=schemas.Agendamento)
def read_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    return AgendamentoService.get_agendamento_by_id(db, agendamento_id)

@router.get("/data/{data}", response_model=List[schemas.Agendamento])
def read_agendamentos_by_data(data: str, db: Session = Depends(get_db)):
    return AgendamentoService.get_agendamentos_by_data(db, data)

@router.get("/cliente/{cliente_id}", response_model=List[schemas.Agendamento])
def read_agendamentos_by_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return AgendamentoService.get_agendamentos_by_cliente(db, cliente_id)

@router.get("/slots-livres/{data}")
def get_slots_livres(data: str, db: Session = Depends(get_db)):
    return AgendamentoService.get_slots_livres(db, data)

@router.put("/{agendamento_id}", response_model=schemas.Agendamento)
def update_agendamento(agendamento_id: int, agendamento: schemas.AgendamentoUpdate, db: Session = Depends(get_db)):
    return AgendamentoService.update_agendamento(db, agendamento_id, agendamento)

@router.patch("/{agendamento_id}/cancel", response_model=schemas.Agendamento)
def cancel_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    return AgendamentoService.cancel_agendamento(db, agendamento_id)

@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    AgendamentoService.delete_agendamento(db, agendamento_id)

@router.get("/horario-livre/{data}")
def is_horario_livre(data: str, db: Session = Depends(get_db)) -> dict:
    return {"livre": AgendamentoService.is_horario_livre(db, data)}