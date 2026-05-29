from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel
from typing import Optional

# Modelo ORM para AWS Aurora
class ProfesorDB(Base):
    __tablename__ = "profesores"

    id = Column(Integer, primary_key=True, index=True)
    numeroEmpleado = Column(Integer, unique=True, nullable=False)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    horasClase = Column(Integer, nullable=False)

# Esquemas Pydantic Flexibles contra errores 422
class ProfesorBase(BaseModel):
    numeroEmpleado: Optional[int] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    horasClase: Optional[int] = None

class ProfesorCreate(ProfesorBase):
    pass

class ProfesorResponse(BaseModel):
    id: int
    numeroEmpleado: Optional[int] = 0
    nombres: Optional[str] = ""
    apellidos: Optional[str] = ""
    horasClase: Optional[int] = 0

    class Config:
        from_attributes = True