from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from database.models import Usuario, ConfiguracionUsuario
from schemas.auth import RegistroRequest, LoginRequest, TokenResponse, RefreshRequest
from services.auth_service import (hash_password, verify_password,
                                    create_access_token, create_refresh_token, decode_token)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def _tokens(user_id: int) -> dict:
    data = {"sub": str(user_id)}
    return {"access_token": create_access_token(data),
            "refresh_token": create_refresh_token(data),
            "token_type": "bearer"}

@router.post("/registro", response_model=TokenResponse, status_code=201)
async def registro(body: RegistroRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Usuario).where(Usuario.email == body.email))
    if r.scalar_one_or_none():
        raise HTTPException(400, "El correo ya está registrado")
    usuario = Usuario(nombre=body.nombre, email=body.email,
                      hashed_password=hash_password(body.password))
    db.add(usuario)
    await db.flush()
    db.add(ConfiguracionUsuario(usuario_id=usuario.id))
    await db.commit()
    return _tokens(usuario.id)

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Usuario).where(Usuario.email == body.email))
    usuario = r.scalar_one_or_none()
    if not usuario or not verify_password(body.password, usuario.hashed_password):
        raise HTTPException(401, "Credenciales inválidas")
    if not usuario.activo:
        raise HTTPException(403, "Cuenta inactiva")
    return _tokens(usuario.id)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Refresh token inválido")
    r = await db.execute(select(Usuario).where(Usuario.id == int(payload["sub"])))
    usuario = r.scalar_one_or_none()
    if not usuario or not usuario.activo:
        raise HTTPException(401, "Usuario no válido")
    return _tokens(usuario.id)