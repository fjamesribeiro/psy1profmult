from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Boolean, Numeric, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Profissional(Base):
    __tablename__ = "profissional"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    calendar_id = Column(String(255))
    nome = Column(String(255), nullable=False)
    email = Column(String(255))
    telefone = Column(String(50))
    tipo_servico = Column(String(50), nullable=False, default="psicologo")
    ativo = Column(Boolean, default=True, index=True)
    duracao_padrao_minutos = Column(Integer, default=60)
    valor_consulta = Column(Numeric(10, 2))
    dias_trabalho = Column(JSON, default={
        "1": [["08:00", "12:00"], ["13:00", "18:00"]],
        "2": [["08:00", "12:00"], ["13:00", "18:00"]],
        "3": [["08:00", "12:00"], ["13:00", "18:00"]],
        "4": [["08:00", "12:00"], ["13:00", "18:00"]],
        "5": [["08:00", "12:00"], ["13:00", "18:00"]],
        "6": [["08:00", "12:00"]]
    })
    prompt_sistema = Column(Text)
    atende_online = Column(Boolean, nullable=False, default=False)
    senha_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    clientes = relationship("Cliente", back_populates="profissional")
    agendamentos = relationship("Agendamento", back_populates="profissional")
    estados_conversa = relationship("EstadoConversa", back_populates="profissional")


class TipoServicoConfig(Base):
    __tablename__ = "tipo_servico_config"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String(50), nullable=False, unique=True)
    nome_display = Column(String(100), nullable=False)
    campos_extras = Column(JSON, default={})
    validacoes = Column(JSON, default={})
    prompt_padrao = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    session_id = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone_mascara = Column(String)
    profissional_id = Column(BigInteger, ForeignKey("profissional.id", ondelete="RESTRICT"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    profissional = relationship("Profissional", back_populates="clientes")
    agendamentos = relationship("Agendamento", back_populates="cliente")
    estado_conversa = relationship("EstadoConversa", back_populates="cliente", uselist=False)


class EstadoConversa(Base):
    __tablename__ = "estados_conversa"

    session_id = Column(String, ForeignKey("clientes.session_id"), primary_key=True)
    estado_atual = Column(String(100), nullable=False)
    dados_temporarios = Column(JSON)
    ultima_atualizacao = Column(DateTime, default=func.now())
    profissional_id = Column(BigInteger, ForeignKey("profissional.id", ondelete="CASCADE"), index=True)

    # Relationships
    cliente = relationship("Cliente", back_populates="estado_conversa")
    profissional = relationship("Profissional", back_populates="estados_conversa")


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(BigInteger, ForeignKey("clientes.id"), nullable=False)
    profissional_id = Column(BigInteger, ForeignKey("profissional.id", ondelete="RESTRICT"), nullable=False)
    link = Column(String)
    data_inicio = Column(DateTime(timezone=True), nullable=False)
    data_fim = Column(DateTime(timezone=True))
    status = Column(String, default="confirmed", nullable=False)
    cancelled_at = Column(DateTime(timezone=True))
    source = Column(String, default="whatsapp")
    tipo_atendimento = Column(String(20), default="presencial", nullable=False)
    evento_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    cliente = relationship("Cliente", back_populates="agendamentos")
    profissional = relationship("Profissional", back_populates="agendamentos")