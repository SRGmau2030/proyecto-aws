from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

# Importamos la configuración de la base de datos y la dependencia get_db
from database import engine, Base, get_db

# Importamos los modelos de la base de datos y los esquemas de validación
from models.alumno import AlumnoDB, AlumnoCreate, AlumnoResponse
from models.profesor import ProfesorDB, ProfesorCreate, ProfesorResponse
import boto3
from fastapi import File, UploadFile  # Sirve para recibir archivos en los endpoints

app = FastAPI(title="SICEI API - Segunda Entrega")
# Configuración del cliente de AWS S3 para las fotos
s3_client = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = "sicei-alumnos-fotos-mau"
# Configuración de Amazon SNS para Notificaciones
sns_client = boto3.client('sns', region_name='us-east-1')
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:204211162715:notificaciones-sicei" 
# =====================================================================
# SÚPER CRÍTICO: Crear las tablas automáticamente en AWS RDS si  no existen
# =====================================================================
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"mensaje": "SICEI API con Base de Datos Relacional en RDS activa"}

# POST /alumnos/subir-foto -> Sube una imagen a S3 y devuelve su URL pública
@app.post("/alumnos/subir-foto")
def subir_foto_alumno(file: UploadFile = File(...)):
    try:
        # 1. Definir el nombre con el que se guardará el archivo en S3
        nombre_archivo = f"fotos/{file.filename}"
        
        # 2. Subir el archivo directamente al bucket de AWS S3 con permisos de lectura pública
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            nombre_archivo,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )
        
        # 3. Construir la URL pública de la imagen en internet
        url_publica = f"https://{BUCKET_NAME}.s3.amazonaws.com/{nombre_archivo}"
        
        return {"url_foto": url_publica}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivo a S3: {str(e)}")

# ==========================================
# ENDPOINTS PARA ALUMNOS [cite: 76]
# ==========================================

# GET /alumnos -> Listar todos desde la base de datos [cite: 77]
@app.get("/alumnos", response_model=List[AlumnoResponse], status_code=status.HTTP_200_OK)
def obtener_alumnos(db: Session = Depends(get_db)):
    alumnos = db.query(AlumnoDB).all()
    return alumnos

# GET /alumnos/{id} -> Buscar un alumno por su ID en la DB [cite: 79]
@app.get("/alumnos/{id}", response_model=AlumnoResponse)
def obtener_alumno_por_id(id: int, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

# POST /alumnos -> Crear un nuevo registro en la DB y notificar por SNS
@app.post("/alumnos", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
def crear_alumno(alumno: AlumnoCreate, db: Session = Depends(get_db)):
    # 1. Crear el objeto con todos sus campos (incluyendo la foto)
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
    
    # 2. DISPARAR NOTIFICACIÓN AUTOMÁTICA POR AMAZON SNS
    try:
        mensaje_alerta = (
            f"¡Alerta SICEI! Se ha registrado un nuevo alumno con éxito.\n\n"
            f"• Nombre: {nuevo_alumno.nombres} {nuevo_alumno.apellidos}\n"
            f"• Matrícula: {nuevo_alumno.matricula}\n"
            f"• Promedio: {nuevo_alumno.promedio}\n"
            f"• Foto URL: {nuevo_alumno.foto}\n"
        )
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensaje_alerta,
            Subject="Nuevo Alumno Registrado - SICEI API"
        )
    except Exception as e:
        # Si falla SNS por algo, imprimimos el error pero dejamos que la API responda 201
        print(f"Error al enviar notificación SNS: {str(e)}")

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
    alumno.foto = alumno_actualizado.foto  
    
    db.commit()
    db.refresh(alumno)
    return alumno

# DELETE /alumnos/{id} -> Borrar el registro físicamente de la DB [cite: 82]
@app.delete("/alumnos/{id}", status_code=status.HTTP_200_OK)
def eliminar_alumno(id: int, db: Session = Depends(get_db)):
    alumno = db.query(AlumnoDB).filter(AlumnoDB.id == id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado para eliminar")
    
    db.delete(alumno)
    db.commit()
    return {"mensaje": f"Alumno con ID {id} eliminado exitosamente de la base de datos"}


# ==========================================
# ENDPOINTS PARA PROFESORES [cite: 76]
# ==========================================

# GET /profesores -> Listar todos [cite: 84]
@app.get("/profesores", response_model=List[ProfesorResponse], status_code=status.HTTP_200_OK)
def obtener_profesores(db: Session = Depends(get_db)):
    profesores = db.query(ProfesorDB).all()
    return profesores

# GET /profesores/{id} -> Buscar por ID [cite: 85]
@app.get("/profesores/{id}", response_model=ProfesorResponse)
def obtener_profesor_por_id(id: int, db: Session = Depends(get_db)):
    profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor

# POST /profesores -> Crear [cite: 86]
@app.post("/profesores", response_model=ProfesorResponse, status_code=status.HTTP_201_CREATED)
def crear_profesor(profesor: ProfesorCreate, db: Session = Depends(get_db)):
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

# PUT /profesores/{id} -> Actualizar [cite: 87]
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
    return profesor_actualizado

# DELETE /profesores/{id} -> Eliminar [cite: 88]
@app.delete("/profesores/{id}", status_code=status.HTTP_200_OK)
def eliminar_profesor(id: int, db: Session = Depends(get_db)):
    profesor = db.query(ProfesorDB).filter(ProfesorDB.id == id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado para eliminar")
    
    db.delete(profesor)
    db.commit()
    return {"mensaje": f"Profesor con ID {id} eliminado exitosamente de la base de datos"}