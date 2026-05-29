from sqlalchemy import Column, Integer, String, Float
from database import Base
from pydantic import BaseModel, Field

# Modelo del ORM (Para crear la tabla en la base de datos de AWS)
class AlumnoDB(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True) # Autogenerado por la DB
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    matricula = Column(String, nullable=False)
    promedio = Column(Float, nullable=False)
    foto = Column(String(255), nullable=True)

# Esquema Pydantic (Para validar los datos que entran en las peticiones de la API)
class AlumnoBase(BaseModel):
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: float = Field(..., ge=0.0, le=100.0)
    foto: str = Field(None)

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoResponse(AlumnoBase):
    id: int

    class Config:
        from_attributes = True