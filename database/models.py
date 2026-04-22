"""
Modelos SQLAlchemy — MotoApp
Tablas: usuarios, vehiculos, mantenimiento (20 módulos), historial, configuracion
"""
from datetime import datetime
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base


# ══════════════════════════════════════════════════
# USUARIOS
# ══════════════════════════════════════════════════
class Usuario(Base):
    __tablename__ = "usuarios"

    id:              Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    nombre:          Mapped[str]      = mapped_column(String(100))
    email:           Mapped[str]      = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(200))
    foto:             Mapped[str | None]  = mapped_column(Text, nullable=True)
    activo:          Mapped[bool]     = mapped_column(Boolean, default=True)
    creado_en:       Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    actualizado_en:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                       onupdate=datetime.utcnow)

    vehiculos:      Mapped[list["Vehiculo"]]      = relationship(back_populates="usuario",
                                                                  cascade="all, delete-orphan")
    configuracion:  Mapped["ConfiguracionUsuario"] = relationship(back_populates="usuario",
                                                                   cascade="all, delete-orphan",
                                                                   uselist=False)
    historial:      Mapped[list["HistorialEvento"]] = relationship(back_populates="usuario",
                                                                    cascade="all, delete-orphan")


# ══════════════════════════════════════════════════
# VEHÍCULOS
# ══════════════════════════════════════════════════
class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    usuario_id:  Mapped[int]      = mapped_column(ForeignKey("usuarios.id"), index=True)
    placa:       Mapped[str]      = mapped_column(String(20), index=True)
    marca:       Mapped[str]      = mapped_column(String(100))
    modelo:      Mapped[str]      = mapped_column(String(100))
    anio:        Mapped[int]      = mapped_column(Integer)
    activo:      Mapped[bool]     = mapped_column(Boolean, default=True)
    creado_en:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    usuario:      Mapped["Usuario"]              = relationship(back_populates="vehiculos")
    mantenimiento: Mapped["Mantenimiento"]       = relationship(back_populates="vehiculo",
                                                                 cascade="all, delete-orphan",
                                                                 uselist=False)
    historial:    Mapped[list["HistorialEvento"]] = relationship(back_populates="vehiculo",
                                                                  cascade="all, delete-orphan")


# ══════════════════════════════════════════════════
# MANTENIMIENTO — todos los módulos en una sola tabla JSONB
# ══════════════════════════════════════════════════
class Mantenimiento(Base):
    """
    Cada módulo se guarda como columna JSON independiente.
    Permite agregar campos sin migraciones de esquema.
    """
    __tablename__ = "mantenimiento"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    vehiculo_id: Mapped[int]      = mapped_column(ForeignKey("vehiculos.id"), unique=True, index=True)

    # ── Motor ──────────────────────────────────
    aceite:          Mapped[dict] = mapped_column(JSON, default=dict)
    filtro_aire:     Mapped[dict] = mapped_column(JSON, default=dict)
    filtro_aceite:   Mapped[dict] = mapped_column(JSON, default=dict)

    # ── Kit de arrastre ────────────────────────
    cadena:   Mapped[dict] = mapped_column(JSON, default=dict)
    pinon:    Mapped[dict] = mapped_column(JSON, default=dict)
    sprocket: Mapped[dict] = mapped_column(JSON, default=dict)

    # ── Frenos y fluidos ───────────────────────
    pastillas_freno:      Mapped[dict] = mapped_column(JSON, default=dict)
    liquido_frenos:       Mapped[dict] = mapped_column(JSON, default=dict)
    liquido_refrigerante: Mapped[dict] = mapped_column(JSON, default=dict)

    # ── Eléctrico ──────────────────────────────
    bujias:               Mapped[dict] = mapped_column(JSON, default=dict)
    bateria:              Mapped[dict] = mapped_column(JSON, default=dict)
    bombilla_principal:   Mapped[dict] = mapped_column(JSON, default=dict)
    bombillas_secundarias:Mapped[dict] = mapped_column(JSON, default=dict)

    # ── Transmisión y cables ───────────────────
    guaya_clutch:     Mapped[dict] = mapped_column(JSON, default=dict)
    guaya_acelerador: Mapped[dict] = mapped_column(JSON, default=dict)
    lineas_freno:     Mapped[dict] = mapped_column(JSON, default=dict)

    # ── Llantas y otros ────────────────────────
    llantas:       Mapped[dict] = mapped_column(JSON, default=dict)
    llantas_aire:  Mapped[dict] = mapped_column(JSON, default=dict)
    bomba_aceite:  Mapped[dict] = mapped_column(JSON, default=dict)
    categoria_mantenimiento: Mapped[dict] = mapped_column(JSON, default=dict)

    actualizado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,
                                                      onupdate=datetime.utcnow)

    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="mantenimiento")


# ══════════════════════════════════════════════════
# HISTORIAL DE EVENTOS
# ══════════════════════════════════════════════════
class HistorialEvento(Base):
    __tablename__ = "historial_eventos"

    id:          Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    usuario_id:  Mapped[int]      = mapped_column(ForeignKey("usuarios.id"), index=True)
    vehiculo_id: Mapped[int]      = mapped_column(ForeignKey("vehiculos.id"), index=True)
    modulo:      Mapped[str]      = mapped_column(String(50))   # "aceite", "cadena", etc.
    titulo:      Mapped[str]      = mapped_column(String(200))
    descripcion: Mapped[str]      = mapped_column(Text, default="")
    kilometraje: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha_evento: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    datos_extra:  Mapped[dict]    = mapped_column(JSON, default=dict)

    usuario:  Mapped["Usuario"]  = relationship(back_populates="historial")
    vehiculo: Mapped["Vehiculo"] = relationship(back_populates="historial")


# ══════════════════════════════════════════════════
# TOKENS DE RESET DE CONTRASEÑA
# ══════════════════════════════════════════════════
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[int]      = mapped_column(ForeignKey("usuarios.id"), index=True)
    token:      Mapped[str]      = mapped_column(String(64), unique=True, index=True)
    usado:      Mapped[bool]     = mapped_column(Boolean, default=False)
    expira_en:  Mapped[datetime] = mapped_column(DateTime)
    creado_en:  Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ══════════════════════════════════════════════════
# CONFIGURACIÓN POR USUARIO
# ══════════════════════════════════════════════════
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