from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from database.connection import get_db
from database.models import Usuario, ConfiguracionUsuario
from schemas.usuario import UsuarioOut, ConfiguracionOut, ConfiguracionUpdate
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


class PerfilUpdate(BaseModel):
    nombre: str | None = None
    foto: str | None = None


@router.get("/me", response_model=UsuarioOut)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.patch("/me/perfil")
async def update_perfil(
    body: PerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.nombre:
        current_user.nombre = body.nombre
    await db.commit()
    await db.refresh(current_user)
    return {"ok": True, "nombre": current_user.nombre}


@router.get("/me/configuracion", response_model=ConfiguracionOut)
async def get_config(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ConfiguracionUsuario).where(
        ConfiguracionUsuario.usuario_id == current_user.id))
    cfg = r.scalar_one_or_none()
    if not cfg:
        cfg = ConfiguracionUsuario(usuario_id=current_user.id)
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)
    return cfg


@router.patch("/me/configuracion", response_model=ConfiguracionOut)
async def update_config(
    body: ConfiguracionUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ConfiguracionUsuario).where(
        ConfiguracionUsuario.usuario_id == current_user.id))
    cfg = r.scalar_one_or_none() or ConfiguracionUsuario(usuario_id=current_user.id)
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(cfg, k, v)
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    return cfg
