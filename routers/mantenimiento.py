from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from database.models import Usuario, Vehiculo, Mantenimiento, HistorialEvento
from schemas.mantenimiento import ModuloUpdate, MantenimientoOut, HistorialCreate, HistorialOut
from middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/vehiculos/{vehiculo_id}/mantenimiento", tags=["Mantenimiento"])

MODULOS = {
    "aceite","filtro_aire","filtro_aceite","cadena","pinon","sprocket",
    "pastillas_freno","liquido_frenos","liquido_refrigerante","bujias",
    "bateria","bombilla_principal","bombillas_secundarias","guaya_clutch",
    "guaya_acelerador","lineas_freno","llantas","llantas_aire",
    "bomba_aceite","categoria_mantenimiento",
}

async def _get_mant(vid: int, uid: int, db: AsyncSession):
    r = await db.execute(select(Vehiculo).where(Vehiculo.id == vid, Vehiculo.usuario_id == uid))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "Vehículo no encontrado")
    m = await db.execute(select(Mantenimiento).where(Mantenimiento.vehiculo_id == vid))
    mant = m.scalar_one_or_none()
    if not mant:
        mant = Mantenimiento(vehiculo_id=vid)
        db.add(mant)
        await db.flush()
    return mant

@router.get("/", response_model=MantenimientoOut)
async def get_mant(vehiculo_id: int,
                   current_user: Usuario = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    return await _get_mant(vehiculo_id, current_user.id, db)

@router.patch("/{modulo}", response_model=MantenimientoOut)
async def actualizar(vehiculo_id: int, modulo: str, body: ModuloUpdate,
                     current_user: Usuario = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    if modulo not in MODULOS:
        raise HTTPException(400, f"Módulo '{modulo}' no válido")
    mant = await _get_mant(vehiculo_id, current_user.id, db)
    setattr(mant, modulo, body.datos)
    db.add(HistorialEvento(
        usuario_id=current_user.id, vehiculo_id=vehiculo_id, modulo=modulo,
        titulo=f"Actualización: {modulo.replace('_',' ').title()}", datos_extra=body.datos,
    ))
    await db.commit()
    await db.refresh(mant)
    return mant

@router.get("/historial/", response_model=list[HistorialOut])
async def historial(vehiculo_id: int, modulo: str | None = None, limite: int = 50,
                    current_user: Usuario = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    q = select(HistorialEvento).where(
        HistorialEvento.vehiculo_id == vehiculo_id,
        HistorialEvento.usuario_id == current_user.id,
    ).order_by(HistorialEvento.fecha_evento.desc()).limit(limite)
    if modulo:
        q = q.where(HistorialEvento.modulo == modulo)
    r = await db.execute(q)
    return r.scalars().all()

@router.post("/historial/", response_model=HistorialOut, status_code=201)
async def crear_evento(vehiculo_id: int, body: HistorialCreate,
                       current_user: Usuario = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Vehiculo).where(
        Vehiculo.id == vehiculo_id, Vehiculo.usuario_id == current_user.id))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "Vehículo no encontrado")
    ev = HistorialEvento(usuario_id=current_user.id, vehiculo_id=vehiculo_id, **body.model_dump())
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return ev