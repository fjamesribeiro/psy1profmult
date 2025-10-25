# ============================================
# 3. auth_service.py - Router de autenticação
# ============================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.auth_service import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_current_profissional
)

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login(
        credentials: schemas.ProfissionalLogin,
        db: Session = Depends(get_db)
):
    """
    Endpoint de login - retorna access token e refresh token.

    O n8n deve chamar este endpoint uma vez no início do fluxo
    e armazenar os tokens para uso nas próximas chamadas.
    """
    # Busca profissional por email
    profissional = db.query(models.Profissional).filter(
        models.Profissional.id == credentials.id,
        models.Profissional.ativo == True
    ).first()

    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    if not hasattr(profissional, 'senha_hash') or not verify_password(credentials.password, profissional.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )

    # Cria tokens
    access_token = create_access_token(data={"sub": str(profissional.id)})
    refresh_token = create_refresh_token(data={"sub": str(profissional.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.AccessToken)
def refresh_access_token(token_data: schemas.TokenRefresh):
    """
    Endpoint para renovar o access token usando o refresh token.

    Quando o access token expirar (após 30 minutos), o n8n pode
    chamar este endpoint com o refresh token para obter um novo access token.
    """
    payload = decode_refresh_token(token_data.refresh_token)
    profissional_id = payload.get("sub")

    if profissional_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    # Cria novo access token
    new_access_token = create_access_token(data={"sub": profissional_id})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=schemas.ProfissionalResponse)
def get_current_user_info(
        profissional: models.Profissional = Depends(get_current_profissional)
):
    """
    Endpoint para obter informações do profissional autenticado.
    Útil para testar se o token está funcionando.
    """
    return {"nome": profissional.nome}