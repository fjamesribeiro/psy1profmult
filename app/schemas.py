from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClienteBase(BaseModel):
    nome: str
    session_id: str
    telefone: str
    email: str
    telefone_mascara: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    nome: Optional[str] = None
    session_id: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

class Cliente(ClienteBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AgendamentoBase(BaseModel):
    cliente_id: int
    link: Optional[str] = None
    data_inicio: datetime
    data_fim: Optional[datetime] = None
    status: str = "confirmed"
    source: str = "whatsapp"
    evento_id: str

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoUpdate(AgendamentoBase):
    cliente_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    status: Optional[str] = None
    source: Optional[str] = None
    evento_id: Optional[str] = None

class Agendamento(AgendamentoBase):
    id: int
    cancelled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProfissionalLogin(BaseModel):
    id: int
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"