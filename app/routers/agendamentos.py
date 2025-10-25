from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas
from app.database import get_db
from app.services.agendamento_service import AgendamentoService
from app.services.auth_service import get_current_profissional

router = APIRouter()

def get_profissional_id(current_professional = Depends(get_current_profissional)) -> int:
    return current_professional.id

@router.post("/", response_model=schemas.Agendamento, status_code=status.HTTP_201_CREATED)
def create_agendamento(
    agendamento: schemas.AgendamentoCreate,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Cria um novo agendamento para o profissional autenticado"""
    return AgendamentoService.create_agendamento(db, profissional_id, agendamento)

@router.get("/", response_model=List[schemas.Agendamento])
def read_agendamentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Lista todos os agendamentos do profissional autenticado"""
    return AgendamentoService.get_agendamentos(db, profissional_id, skip, limit)

@router.get("/{agendamento_id}", response_model=schemas.Agendamento)
def read_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Busca um agendamento específico do profissional autenticado"""
    return AgendamentoService.get_agendamento_by_id(db, profissional_id, agendamento_id)

@router.get("/data/{data}", response_model=List[schemas.Agendamento])
def read_agendamentos_by_data(
    data: str,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Lista agendamentos de uma data específica do profissional autenticado"""
    return AgendamentoService.get_agendamentos_by_data(db, profissional_id, data)

@router.get("/cliente/{cliente_id}", response_model=List[schemas.Agendamento])
def read_agendamentos_by_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Lista agendamentos de um cliente específico do profissional autenticado"""
    return AgendamentoService.get_agendamentos_by_cliente(db, profissional_id, cliente_id)

@router.get("/slots-livres/{data}")
def get_slots_livres(
    data: str,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Retorna slots livres para uma data específica do profissional autenticado"""
    return AgendamentoService.get_slots_livres(db, profissional_id, data)

@router.put("/{agendamento_id}", response_model=schemas.Agendamento)
def update_agendamento(
    agendamento_id: int,
    agendamento: schemas.AgendamentoUpdate,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Atualiza um agendamento do profissional autenticado"""
    return AgendamentoService.update_agendamento(db, profissional_id, agendamento_id, agendamento)

@router.patch("/{agendamento_id}/cancel", response_model=schemas.Agendamento)
def cancel_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Cancela um agendamento do profissional autenticado"""
    return AgendamentoService.cancel_agendamento(db, profissional_id, agendamento_id)

@router.delete("/{agendamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agendamento(
    agendamento_id: int,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
):
    """Deleta um agendamento do profissional autenticado"""
    AgendamentoService.delete_agendamento(db, profissional_id, agendamento_id)

@router.get("/horario-livre/{data}")
def is_horario_livre(
    data: str,
    db: Session = Depends(get_db),
    profissional_id: int = Depends(get_profissional_id)
) -> dict:
    """Verifica se um horário específico está livre para o profissional autenticado"""
    return {"livre": AgendamentoService.is_horario_livre(db, profissional_id, data)}

@router.get("/proximo-estado/{estado_atual}")
def get_proximo_estado(estado_atual: str) -> dict:
    """Retorna o próximo estado no fluxo de agendamento"""
    return {"proximo_estado": AgendamentoService.proximo_estado(estado_atual)}