from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Conductor(Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    licencia = Column(String(50), unique=True, index=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    estado = Column(String(20), default="disponible", nullable=False)

    vehiculos = relationship("Vehiculo", back_populates="conductor")


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    placa = Column(String(20), unique=True, index=True, nullable=False)
    marca = Column(String(50), nullable=False)
    capacidad_kg = Column(Float, nullable=False)
    conductor_id = Column(Integer, ForeignKey("conductores.id"), nullable=False)

    conductor = relationship("Conductor", back_populates="vehiculos")
