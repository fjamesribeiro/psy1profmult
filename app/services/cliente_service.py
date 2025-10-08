from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List
from app import models
from app import schemas

class ClienteService:
    
    @staticmethod
    def create_cliente(db: Session, cliente: schemas.ClienteCreate) -> models.Cliente:
        try:
            db_cliente = models.Cliente(**cliente.model_dump())
            db.add(db_cliente)
            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Session ID already exists")
    
    @staticmethod
    def get_clientes(db: Session, skip: int = 0, limit: int = 100) -> List[models.Cliente]:
        return db.query(models.Cliente).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_cliente_by_id(db: Session, cliente_id: int) -> models.Cliente:
        cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente not found")
        return cliente
    
    @staticmethod
    def get_cliente_by_email(db: Session, email: str) -> models.Cliente:
        cliente = db.query(models.Cliente).filter(models.Cliente.email == email).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente not found")
        return cliente
    
    @staticmethod
    def update_cliente(db: Session, cliente_id: int, cliente: schemas.ClienteUpdate) -> models.Cliente:
        db_cliente = ClienteService.get_cliente_by_id(db, cliente_id)
        
        update_data = cliente.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_cliente, key, value)
        
        try:
            db.commit()
            db.refresh(db_cliente)
            return db_cliente
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Session ID already exists")
    
    @staticmethod
    def delete_cliente(db: Session, cliente_id: int):
        db_cliente = ClienteService.get_cliente_by_id(db, cliente_id)
        
        agendamentos_count = db.query(models.Agendamento).filter(
            models.Agendamento.cliente_id == cliente_id
        ).count()
        
        if agendamentos_count > 0:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete cliente with existing agendamentos"
            )
        
        db.delete(db_cliente)
        db.commit()