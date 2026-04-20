from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id:              Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    nombre:          Mapped[str]      = mapped_column(String(100))
    email:           Mapped[str]      = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(200))
    activo:          Mapped[bool]     = mapped_column(Boolean, default=True)
    creado_en:       Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    actualizado_en:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                       onupdate=datetime.utcnow)
    vehiculos:     Mapped[list["Vehiculo"]]       = relationship(back_populates="usuario",
                                                                   cascade="all, delete-orphan")
    configuracion: Mapped["ConfiguracionUsuario"] = relationship(back_populates="usuario",
                                                                   cascade="all, delete-orphan",
                                                                   uselist=False)
    historial:     Mapped[list["HistorialEvento"]] = relationship(back_populates="usuario",
                                                                    cascade="all, delete-orphan")

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int]      = mapped_column(ForeignKey("usuarios.id"), index=True)
    placa:      Mapped[str]      = mapped_column(String(20), index=True)
    marca:      Mapped[str]      = mapped_column(String(100))
    modelo:     Mapped[str]      = mapped_column(String(100))
    anio:       Mapped[int]      = mapped_column(Integer)
    activo:     Mapped[bool]     = mapped_column(Boolean, default=True)
    creado_en:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    usuario:       Mapped["Usuario"]               = relationship(back_populates="vehiculos")
    mantenimiento: Mapped["Mantenimiento"]          = relationship(back_populates="vehiculo",
                                                                    cascade="all, delete-orphan",
                                                                    uselist=False)
    historial:     Mapped[list["HistorialEvento"]]  = relationship(back_populates="vehiculo",
                                                                    cascade="all, delete-orphan")

class Mantenimiento(Base):
    __tablename__ = "mantenimiento"
    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    vehiculo_id: Mapped[int]      = mapped_column(ForeignKey("vehiculos.id"), unique=True, index=True)
    aceite:                   Mapped[dict] = mapped_column(JSON, default=dict)
    filtro_aire:              Mapped[dict] = mapped_column(JSON, default=dict)
    filtro_aceite:            Mapped[dict] = mapped_column(JSON, default=dict)
    cadena:                   Mapped[dict] = mapped_column(JSON, default=dict)
    pinon:                    Mapped[dict] = mapped_column(JSON, default=dict)
    sprocket:                 Mapped[dict] = mapped_column(JSON, default=dict)
    pastillas_freno:          Mapped[dict] = mapped_column(JSON, default=dict)
    liquido_frenos:           Mapped[dict] = mapped_column(JSON, default=dict)
    liquido_refrigerante:     Mapped[dict] = mapped_column(JSON, default=dict)
    bujias:                   Mapped[dict] = mapped_column(JSON, default=dict)
    bateria:                  Mapped[dict] = mapped_column(JSON, default=dict)
    bombilla_principal:       Mapped[dict] = mapped_column(JSON, default=dict)
    bombillas_secundarias:    Mapped[dict] = mapped_column(JSON, default=dict)
    guaya_clutch:             Mapped[dict] = mapped_column(JSON, default=dict)
    guaya_acelerador:         Mapped[dict] = mapped_column(JSON, default=dict)
    lineas_freno:             Mapped[dict] = mapped_column(JSON, default=dict)
    llantas:                  Mapped[dict] = mapped_column(JSON, default=dict)
    llantas_aire:             Mapped[dict] = mapped_column(JSON, default=dict)
    bomba_aceite:             Mapped[dict] = mapped_column(JSON, default=dict)
    categoria_mantenimiento:  Mapped[dict] = mapped_column(JSON, default=dict)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                      onupdate=datetime.utcnow)
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="mantenimiento")

class HistorialEvento(Base):
    __tablename__ = "historial_eventos"
    id:           Mapped[int]       = mapped_column(Integer, primary_key=True, index=True)
    usuario_id:   Mapped[int]       = mapped_column(ForeignKey("usuarios.id"), index=True)
    vehiculo_id:  Mapped[int]       = mapped_column(ForeignKey("vehiculos.id"), index=True)
    modulo:       Mapped[str]       = mapped_column(String(50))
    titulo:       Mapped[str]       = mapped_column(String(200))
    descripcion:  Mapped[str]       = mapped_column(Text, default="")
    kilometraje:  Mapped[float|None]= mapped_column(Float, nullable=True)
    fecha_evento: Mapped[datetime]  = mapped_column(DateTime, default=datetime.utcnow)
    datos_extra:  Mapped[dict]      = mapped_column(JSON, default=dict)
    usuario:  Mapped["Usuario"]  = relationship(back_populates="historial")
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="historial")

class ConfiguracionUsuario(Base):
    __tablename__ = "configuracion_usuarios"
    id:                    Mapped[int]  = mapped_column(Integer, primary_key=True, index=True)
    usuario_id:            Mapped[int]  = mapped_column(ForeignKey("usuarios.id"), unique=True)
    notificaciones_push:   Mapped[bool] = mapped_column(Boolean, default=True)
    alertas_mantenimiento: Mapped[bool] = mapped_column(Boolean, default=True)
    alertas_combustible:   Mapped[bool] = mapped_column(Boolean, default=True)
    alertas_documentos:    Mapped[bool] = mapped_column(Boolean, default=False)
    compartir_ubicacion:   Mapped[bool] = mapped_column(Boolean, default=False)
    idioma:                Mapped[str]  = mapped_column(String(10), default="es")
    unidades:              Mapped[str]  = mapped_column(String(20), default="km")
    moneda:                Mapped[str]  = mapped_column(String(10), default="COP")
    usuario: Mapped["Usuario"] = relationship(back_populates="configuracion")