from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    session_id = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone_mascara = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    agendamentos = relationship("Agendamento", back_populates="cliente")

class Agendamento(Base):
    __tablename__ = "agendamentos"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(BigInteger, ForeignKey("clientes.id"), nullable=False)
    link = Column(String)
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True))
    status = Column(String, default="confirmed", nullable=False)
    cancelled_at = Column(DateTime(timezone=True))
    source = Column(String, default="whatsapp")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    evento_id = Column(String, unique=True, nullable=False)
    
    cliente = relationship("Cliente", back_populates="agendamentos")