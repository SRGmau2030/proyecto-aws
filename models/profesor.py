from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel, Field

# Modelo del ORM
class ProfesorDB(Base):
    __tablename__ = "profesores"

    id = Column(Integer, primary_key=True, index=True) # Autogenerado por la DB
    numeroEmpleado = Column(String, nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    horasClase = Column(Integer, nullable=False)

# Esquema Pydantic
class ProfesorBase(BaseModel):
    numeroEmpleado: str = Field(..., min_length=1)
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    horasClase: int = Field(..., ge=0)

class ProfesorCreate(ProfesorBase):
    pass

class ProfesorResponse(ProfesorBase):
    id: int

    class Config:
        from_attributes = True