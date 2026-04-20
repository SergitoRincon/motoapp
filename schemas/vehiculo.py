from datetime import datetime
from pydantic import BaseModel

class VehiculoCreate(BaseModel):
    placa: str
    marca: str
    modelo: str
    anio: int

class VehiculoOut(BaseModel):
    id: int
    placa: str
    marca: str
    modelo: str
    anio: int
    activo: bool
    creado_en: datetime
    model_config = {"from_attributes": True}