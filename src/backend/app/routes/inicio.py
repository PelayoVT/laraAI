import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal

router = APIRouter()

# Obtenemos la sesion de la bbdd
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/inicio")
def iniciar_sesion(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Verificamos que no exista
    if db.query(models.User).filter(models.User.seudonimo == usuario.seudonimo).first():
        raise HTTPException(status_code=400, detail="El seudónimo ya está registrado")

    # Hasheamos contraseña
    hashed_pw = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    nuevo_usuario = models.User(
        seudonimo=usuario.seudonimo,
        password=hashed_pw,
        consentimiento_tratamiento=usuario.consentimiento_tratamiento
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    nueva_conversacion = models.Conversation(user_id=nuevo_usuario.id)
    db.add(nueva_conversacion)
    db.commit()
    db.refresh(nueva_conversacion)

    return {
        "usuario": {
            "id": nuevo_usuario.id,
            "seudonimo": nuevo_usuario.seudonimo,
            "fecha_registro": nuevo_usuario.fecha_registro.isoformat()
        },
        "conversacion_id": nueva_conversacion.id
    }

@router.post("/login")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = db.query(models.User).filter(models.User.seudonimo == usuario.seudonimo).first()

    if not db_usuario or not bcrypt.checkpw(usuario.password.encode('utf-8'), db_usuario.password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {
        "usuario": {
            "id": db_usuario.id,
            "seudonimo": db_usuario.seudonimo,
            "fecha_registro": db_usuario.fecha_registro.isoformat()
        }
    }

