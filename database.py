from typing import List
from models.alumno import Alumno
from models.profesor import Profesor

# Listas globales que simulan nuestra base de datos temporal en memoria
db_alumnos: List[Alumno] = []
db_profesores: List[Profesor] = []