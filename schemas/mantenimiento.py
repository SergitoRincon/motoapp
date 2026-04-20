from datetime import datetime
from pydantic import BaseModel

class ModuloUpdate(BaseModel):
    datos: dict

class MantenimientoOut(BaseModel):
    vehiculo_id: int
    aceite: dict
    filtro_aire: dict
    filtro_aceite: dict
    cadena: dict
    pinon: dict
    sprocket: dict
    pastillas_freno: dict
    liquido_frenos: dict
    liquido_refrigerante: dict
    bujias: dict
    bateria: dict
    bombilla_principal: dict
    bombillas_secundarias: dict
    guaya_clutch: dict
    guaya_acelerador: dict
    lineas_freno: dict
    llantas: dict
    llantas_aire: dict
    bomba_aceite: dict
    categoria_mantenimiento: dict
    actualizado_en: datetime
    model_config = {"from_attributes": True}

class HistorialCreate(BaseModel):
    modulo: str
    titulo: str
    descripcion: str = ""
    kilometraje: float | None = None
    datos_extra: dict = {}

class HistorialOut(BaseModel):
    id: int
    modulo: str
    titulo: str
    descripcion: str
    kilometraje: float | None
    fecha_evento: datetime
    datos_extra: dict
    model_config = {"from_attributes": True}