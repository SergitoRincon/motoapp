from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from database.models import Usuario, Vehiculo, Mantenimiento
from schemas.vehiculo import VehiculoCreate, VehiculoOut
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

async def _vehiculo_o_404(vid: int, uid: int, db: AsyncSession):
    r = await db.execute(select(Vehiculo).where(Vehiculo.id == vid, Vehiculo.usuario_id == uid))
    v = r.scalar_one_or_none()
    if not v:
        raise HTTPException(404, "Vehículo no encontrado")
    return v

@router.get("/", response_model=list[VehiculoOut])
async def listar(current_user: Usuario = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Vehiculo).where(Vehiculo.usuario_id == current_user.id))
    return r.scalars().all()

@router.post("/", response_model=VehiculoOut, status_code=201)
async def crear(body: VehiculoCreate,
                current_user: Usuario = Depends(get_current_user),
                db: AsyncSession = Depends(get_db)):
    v = Vehiculo(**body.model_dump(), usuario_id=current_user.id)
    db.add(v)
    await db.flush()
    db.add(Mantenimiento(vehiculo_id=v.id))
    await db.commit()
    await db.refresh(v)
    return v

@router.delete("/{vehiculo_id}", status_code=204)
async def eliminar(vehiculo_id: int,
                   current_user: Usuario = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    v = await _vehiculo_o_404(vehiculo_id, current_user.id, db)
    await db.delete(v)
    await db.commit()