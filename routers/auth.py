import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from database.connection import get_db
from database.models import Usuario, ConfiguracionUsuario, PasswordResetToken
from schemas.auth import RegistroRequest, LoginRequest, TokenResponse, RefreshRequest
from services.auth_service import (hash_password, verify_password,
                                    create_access_token, create_refresh_token, decode_token)
from services.email_service import enviar_reset_password, enviar_bienvenida
from middleware.auth_middleware import get_current_user

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
    enviar_bienvenida(usuario.email, usuario.nombre)
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


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nuevo: str

@router.patch("/cambiar-password")
async def cambiar_password(
    body: CambiarPasswordRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.password_actual, current_user.hashed_password):
        raise HTTPException(400, "La contraseña actual es incorrecta")
    current_user.hashed_password = hash_password(body.password_nuevo)
    await db.commit()
    return {"ok": True, "mensaje": "Contraseña actualizada correctamente"}


class SolicitarResetRequest(BaseModel):
    email: str

@router.post("/solicitar-reset")
async def solicitar_reset(body: SolicitarResetRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Usuario).where(Usuario.email == body.email))
    usuario = r.scalar_one_or_none()
    if not usuario:
        return {"ok": True, "mensaje": "Si el correo existe, recibirás un código"}
    token = str(secrets.randbelow(900000) + 100000)
    expira = datetime.utcnow() + timedelta(minutes=15)
    db.add(PasswordResetToken(
        usuario_id=usuario.id, token=token, expira_en=expira))
    await db.commit()
    enviado = enviar_reset_password(usuario.email, usuario.nombre, token)
    return {"ok": True, "mensaje": "Código enviado a tu correo"}


class ConfirmarResetRequest(BaseModel):
    email: str
    codigo: str
    password_nuevo: str

@router.post("/confirmar-reset")
async def confirmar_reset(body: ConfirmarResetRequest, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Usuario).where(Usuario.email == body.email))
    usuario = r.scalar_one_or_none()
    if not usuario:
        raise HTTPException(400, "Correo no encontrado")
    r2 = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.usuario_id == usuario.id,
            PasswordResetToken.token == body.codigo,
            PasswordResetToken.usado == False,
            PasswordResetToken.expira_en > datetime.utcnow(),
        )
    )
    reset_token = r2.scalar_one_or_none()
    if not reset_token:
        raise HTTPException(400, "Código inválido o expirado")
    reset_token.usado = True
    usuario.hashed_password = hash_password(body.password_nuevo)
    await db.commit()
    return {"ok": True, "mensaje": "Contraseña actualizada correctamente"}
