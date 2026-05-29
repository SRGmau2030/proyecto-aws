from sqlalchemy import Column, Integer, String, Float
from database import Base
from pydantic import BaseModel, Field
from typing import Optional

# Modelo ORM para AWS Aurora
class AlumnoDB(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    matricula = Column(String(10), nullable=False)
    promedio = Column(Float, nullable=False)
    foto = Column(String(255), nullable=True)

# Esquemas Pydantic Flexibles contra errores 422
class AlumnoBase(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    matricula: Optional[str] = None
    promedio: Optional[float] = None
    foto: Optional[str] = None

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoResponse(BaseModel):
    id: int
    nombres: Optional[str] = ""
    apellidos: Optional[str] = ""
    matricula: Optional[str] = ""
    promedio: Optional[float] = 0.0
    foto: Optional[str] = None

    class Config:
        from_attributes = True