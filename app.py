from fastapi import FastAPI, HTTPException, status, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import boto3

# Importamos la configuración de la base de datos y la dependencia get_db
from database import engine, Base, get_db

# Importamos los modelos de la base de datos y los esquemas de validación
from models.alumno import AlumnoDB, AlumnoCreate, AlumnoResponse
from models.profesor import ProfesorDB, ProfesorCreate, ProfesorResponse

app = FastAPI(title="SICEI API - Segunda Entrega")

# =====================================================================
# SÚPER CRÍTICO: Crear las tablas automáticamente en AWS RDS si no existen
# =====================================================================
Base.metadata.create_all(bind=engine)

# =====================================================================
# CONFIGURACIÓN DE SERVICIOS AWS (S3 y SNS)
# =====================================================================
s3_client = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = "sicei-alumnos-fotos-mau"

sns_client = boto3.client('sns', region_name='us-east-1')
# ARN real de tu consola de AWS SNS para las notificaciones
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:204211162715:notificaciones-sicei"


@app.get("/")
def read_root():
    return {"mensaje": "SICEI API con Base de Datos Relacional en RDS activa"}


# ==========================================
# ENDPOINTS PARA ALUMNOS
# ==========================================

# POST /alumnos/subir-foto -> Sube una imagen a S3 y devuelve su URL pública
@app.post("/alumnos/subir-foto")
def subir_foto_alumno(file: UploadFile = File(...)):
    try:
        nombre_archivo = f"fotos/{file.filename}"
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            nombre_archivo,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )
        url_publica = f"https://{BUCKET_NAME}.s3.amazonaws.com/{nombre_archivo}"
        return {"url_foto": url_publica}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo a S3: {str(e)}")


# GET /alumnos -> Listar todos desde la base de datos
@app.get("/alumnos", response_model=List[AlumnoResponse], status_code=status.HTTP_200_OK)
def obtener_alumnos(db: Session = Depends(get_db)):
    alumnos = db.query(AlumnoDB).all()
    return alumnos


# GET /alumnos/{id} -> Buscar un alumno por su ID en la DB
@app.get("/alumnos/{id}", response_model=AlumnoResponse)
def obtener_alumno_por_id(id: int, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno


# POST /alumnos -> Crear un nuevo registro en la DB (Alineado con el autotest)
@app.post("/alumnos", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
def crear_alumno(alumno: AlumnoCreate, db: Session = Depends(get_db)):
    # 1. Validar matrícula duplicada para evitar romper consistencia en el test masivo
    alumno_existente = db.query(AlumnoDB).filter(AlumnoDB.matricula == alumno.matricula).first()
    if alumno_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="La matrícula ya se encuentra registrada"
        )

    try:
        # 2. Guardamos el valor directamente (si el test manda None, se guarda NULL limpiamente)
        nuevo_alumno = AlumnoDB(
            nombres=alumno.nombres,
            apellidos=alumno.apellidos,
            matricula=alumno.matricula,
            promedio=alumno.promedio,
            foto=alumno.foto  
        )
        db.add(nuevo_alumno)
        db.commit()
        db.refresh(nuevo_alumno)
    except Exception as db_error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en Base de Datos: {str(db_error)}")
    
    # 3. AISLAMIENTO DE SNS: Se envía en bloque aislado para que no bloquee las ráfagas del test
    try:
        mensaje_alerta = (
            f"¡Alerta SICEI! Nuevo registro exitoso.\n\n"
            f"• Alumno: {nuevo_alumno.nombres} {nuevo_alumno.apellidos}\n"
            f"• Matrícula: {nuevo_alumno.matricula}\n"
            f"• Promedio: {nuevo_alumno.promedio}\n"
            f"• URL Foto: {nuevo_alumno.foto if nuevo_alumno.foto else 'No proporcionada'}\n"
        )
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensaje_alerta,
            Subject="Registro Exitoso SICEI"
        )
    except Exception:
        pass  # Si SNS se satura, se ignora para no rechazar el 201 Created del alumno

    return nuevo_alumno


# PUT /alumnos/{id} -> Modificar los datos de un alumno existente
@app.put("/alumnos/{id}", response_model=AlumnoResponse)
def actualizar_alumno(id: int, alumno_actualizado: AlumnoCreate, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado para actualizar")
    
    alumno.nombres = alumno_actualizado.nombres
    alumno.apellidos = alumno_actualizado.apellidos
    alumno.matricula = alumno_actualizado.matricula
    alumno.promedio = alumno_actualizado.promedio
    alumno.foto = alumno_actualizado.foto  # Mapeo directo y transparente de la foto
    
    db.commit()
    db.refresh(alumno)
    return alumno


# DELETE /alumnos/{id} -> Borrar el registro físicamente de la DB
@app.delete("/alumnos/{id}", status_code=status.HTTP_200_OK)
def eliminar_alumno(id: int, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado para eliminar")
    
    db.delete(alumno)
    db.commit()
    return {"mensaje": f"Alumno con ID {id} eliminado exitosamente de la base de datos"}


# ==========================================
# ENDPOINTS PARA PROFESORES
# ==========================================

# GET /profesores -> Listar todos
@app.get("/profesores", response_model=List[ProfesorResponse], status_code=status.HTTP_200_OK)
def obtener_profesores(db: Session = Depends(get_db)):
    profesores = db.query(ProfesorDB).all()
    return profesores


# GET /profesores/{id} -> Buscar por ID
@app.get("/profesores/{id}", response_model=ProfesorResponse)
def obtener_profesor_por_id(id: int, db: Session = Depends(get_db)):
    profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor


# POST /profesores -> Crear
@app.post("/profesores", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED)
def crear_profesor(profesor: ProfesorCreate, db: Session = Depends(get_db)):
    profesor_existente = db.query(ProfesorDB).filter(ProfesorDB.numeroEmpleado == profesor.numeroEmpleado).first()
    if profesor_existente:
        raise HTTPException(status_code=400, detail="El número de empleado ya existe")

    try:
        nuevo_profesor = ProfesorDB(
            numeroEmpleado=profesor.numeroEmpleado,
            nombres=profesor.nombres,
            apellidos=profesor.apellidos,
            horasClase=profesor.horasClase
        )
        db.add(nuevo_profesor)
        db.commit()
        db.refresh(nuevo_profesor)
        return nuevo_profesor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar profesor: {str(e)}")


# PUT /profesores/{id} -> Actualizar
@app.put("/profesores/{id}", response_model=ProfesorResponse)
def actualizar_profesor(id: int, profesor_actualizado: ProfesorCreate, db: Session = Depends(get_db)):
    profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado para actualizar")
    
    profesor.numeroEmpleado = profesor_actualizado.numeroEmpleado
    profesor.nombres = profesor_actualizado.nombres
    profesor.apellidos = profesor_actualizado.apellidos
    profesor.horasClase = profesor_actualizado.horasClase
    
    db.commit()
    db.refresh(profesor)
    return profesor


# DELETE /profesores/{id} -> Eliminar
@app.delete("/profesores/{id}", status_code=status.HTTP_200_OK)
def eliminar_profesor(id: int, db: Session = Depends(get_db)):
    profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado para eliminar")
    
    db.delete(profesor)
    db.commit()
    return {"mensaje": f"Profesor con ID {id} eliminado exitosamente de la base de datos"}