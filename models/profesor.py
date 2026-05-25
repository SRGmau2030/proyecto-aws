from pydantic import BaseModel, Field

class Profesor(BaseModel):
    id: int
    numeroEmpleado: str = Field(..., min_length=1)
    nombres: str = Field(..., min_length=1)
    apellidos: str = Field(..., min_length=1)
    horasClase: int = Field(..., ge=0)