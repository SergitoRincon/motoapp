from datetime import datetime
from pydantic import BaseModel, EmailStr

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    activo: bool
    creado_en: datetime
    foto: str | None = None
    model_config = {"from_attributes": True}

class ConfiguracionOut(BaseModel):
    notificaciones_push: bool
    alertas_mantenimiento: bool
    alertas_combustible: bool
    alertas_documentos: bool
    compartir_ubicacion: bool
    idioma: str
    unidades: str
    moneda: str
    model_config = {"from_attributes": True}

class ConfiguracionUpdate(BaseModel):
    notificaciones_push:   bool | None = None
    alertas_mantenimiento: bool | None = None
    alertas_combustible:   bool | None = None
    alertas_documentos:    bool | None = None
    compartir_ubicacion:   bool | None = None
    idioma:   str | None = None
    unidades: str | None = None
    moneda:   str | None = None