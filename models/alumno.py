from sqlalchemy import Column, Integer, String, Float
from database import Base
from pydantic import BaseModel, Field
from typing import Optional

# Modelo ORM (Estructura de la tabla en AWS Aurora)
class AlumnoDB(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    matricula = Column(String(10), nullable=False)
    promedio = Column(Float, nullable=False)
    foto = Column(String(255), nullable=True)  # Permite almacenar NULL de forma nativa

# Esquemas de Validación Pydantic
class AlumnoBase(BaseModel):
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: float = Field(..., ge=0.0, le=100.0)
    foto: Optional[str] = None  # Alivio crítico: Acepta strings o valores nulos (None)

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoResponse(AlumnoBase):
    id: int

    class Config:
        from_attributes = True