from fastapi import FastAPI, HTTPException, status
from typing import List

# Importamos los modelos y los arreglos en memoria
from models.alumno import Alumno
from models.profesor import Profesor
from database import db_alumnos, db_profesores

app = FastAPI(title="SICEI API - Primera Entrega")

@app.get("/")
def read_root():
    return {"mensaje": "SICEI API Modular funcionando"}

# ==========================================
# ENDPOINTS PARA ALUMNOS
# ==========================================

@app.get("/alumnos", response_model=List[Alumno], status_code=status.HTTP_200_OK)
def obtener_alumnos():
    # Si está vacío, FastAPI devuelve automáticamente un arreglo vacío [] con código 200
    return db_alumnos

@app.get("/alumnos/{id}", response_model=Alumno)
def obtener_alumno_por_id(id: int):
    for alumno in db_alumnos:
        if alumno.id == id:
            return alumno
    raise HTTPException(status_code=404, detail="Alumno no encontrado")

@app.post("/alumnos", response_model=Alumno, status_code=status.HTTP_201_CREATED)
def crear_alumno(alumno: Alumno):
    # Validamos que no exista un registro previo con el mismo ID
    for a in db_alumnos:
        if a.id == alumno.id:
            raise HTTPException(status_code=400, detail="El ID de alumno ya existe")
    
    db_alumnos.append(alumno)
    return alumno

@app.put("/alumnos/{id}", response_model=Alumno)
def actualizar_alumno(id: int, alumno_actualizado: Alumno):
    for index, alumno in enumerate(db_alumnos):
        if alumno.id == id:
            db_alumnos[index] = alumno_actualizado
            return alumno_actualizado
    raise HTTPException(status_code=404, detail="Alumno no encontrado para actualizar")

@app.delete("/alumnos/{id}", status_code=status.HTTP_200_OK)
def eliminar_alumno(id: int):
    for index, alumno in enumerate(db_alumnos):
        if alumno.id == id:
            db_alumnos.pop(index)
            return {"mensaje": f"Alumno con ID {id} eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Alumno no encontrado para eliminar")


# ==========================================
# ENDPOINTS PARA PROFESORES
# ==========================================

@app.get("/profesores", response_model=List[Profesor], status_code=status.HTTP_200_OK)
def obtener_profesores():
    return db_profesores

@app.get("/profesores/{id}", response_model=Profesor)
def obtener_profesor_por_id(id: int):
    for profesor in db_profesores:
        if profesor.id == id:
            return profesor
    raise HTTPException(status_code=404, detail="Profesor no encontrado")

@app.post("/profesores", response_model=Profesor, status_code=status.HTTP_201_CREATED)
def crear_profesor(profesor: Profesor):
    for p in db_profesores:
        if p.id == profesor.id:
            raise HTTPException(status_code=400, detail="El ID de profesor ya existe")
    
    db_profesores.append(profesor)
    return profesor

@app.put("/profesores/{id}", response_model=Profesor)
def actualizar_profesor(id: int, profesor_actualizado: Profesor):
    for index, profesor in enumerate(db_profesores):
        if profesor.id == id:
            db_profesores[index] = profesor_actualizado
            return profesor_actualizado
    raise HTTPException(status_code=404, detail="Profesor no encontrado para actualizar")

@app.delete("/profesores/{id}", status_code=status.HTTP_200_OK)
def eliminar_profesor(id: int):
    for index, profesor in enumerate(db_profesores):
        if profesor.id == id:
            db_profesores.pop(index)
            return {"mensaje": f"Profesor con ID {id} eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Profesor no encontrado para eliminar")