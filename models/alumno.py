from pydantic import BaseModel, Field

class Alumno(BaseModel):
    id: int
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    matricula: str = Field(..., min_length=1)
    promedio: float = Field(..., ge=0.0, le=100.0)