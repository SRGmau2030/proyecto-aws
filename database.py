from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Tu URL de conexión usando tu punto de enlace de AWS RDS
# Formato: postgresql://usuario:contraseña@punto_de_enlace:puerto/nombre_db
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Sicei1234*@sicei-db.cluster-c6bi4x5qmnfp.us-east-1.rds.amazonaws.com:5432/postgres"

# 2. Creamos el motor de conexión
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Creamos una sesión para hacer consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Esta clase base servirá para heredar y crear las tablas
Base = declarative_base()

# Dependencia para abrir y cerrar la sesión de la DB en cada endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()