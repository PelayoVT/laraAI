from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from datetime import datetime
from fastapi.responses import FileResponse
import os
from app.utils.pdf import generar_pdf

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def obtener_user_id_desde_header(request: Request) -> int:
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=400, detail="ID de usuario no proporcionado en el encabezado")
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

@router.get("/conversacion/{id}", response_model=list[schemas.MensajeOut])
def obtener_conversacion(id: int, db: Session = Depends(get_db)):
    mensajes = db.query(models.Message).filter(models.Message.conversation_id == id).order_by(models.Message.timestamp).all()
    if not mensajes:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return mensajes

@router.get("/conversaciones/usuario", response_model=list[schemas.ConversacionOut])
def obtener_conversaciones_usuario(request: Request, db: Session = Depends(get_db)):
    user_id = obtener_user_id_desde_header(request)
    return db.query(models.Conversation).filter(models.Conversation.user_id == user_id).order_by(models.Conversation.fecha_inicio.desc()).all()

@router.post("/conversaciones", response_model=schemas.ConversacionOut)
def crear_conversacion(request: Request, db: Session = Depends(get_db)):
    user_id = obtener_user_id_desde_header(request)
    nueva = models.Conversation(
        user_id=user_id,
        fecha_inicio=datetime.utcnow(),
        fecha_fin=None
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.post("/conversaciones/{id}/finalizar")
def finalizar_conversacion(id: int, request: Request, db: Session = Depends(get_db)):
    user_id = obtener_user_id_desde_header(request)
    conversacion = db.query(models.Conversation).filter_by(id=id, user_id=user_id).first()
    if not conversacion:
        raise HTTPException(status_code=404, detail="Conversación no encontrada o no autorizada")
    if conversacion.fecha_fin:
        raise HTTPException(status_code=400, detail="La conversación ya fue finalizada")

    conversacion.cerrada = True
    conversacion.fecha_fin = datetime.utcnow()
    db.commit()
    return {"mensaje": "Conversación finalizada correctamente"}

@router.get("/conversaciones/{id}/exportar", response_class=FileResponse)
def exportar_conversacion(id: int, request: Request, db: Session = Depends(get_db)):
    mensajes = db.query(models.Message).filter(models.Message.conversation_id == id).order_by(models.Message.timestamp).all()
    if not mensajes:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    user_id = obtener_user_id_desde_header(request)
    conversacion = db.query(models.Conversation).filter_by(id=id, user_id=user_id).first()

    if not conversacion or not conversacion.cerrada:
        raise HTTPException(status_code=400, detail="La conversación no ha sido finalizada")

    pdf_path = generar_pdf(id, mensajes)
    conversacion.exportado_pdf = True
    db.commit()

    return FileResponse(path=pdf_path, filename=os.path.basename(pdf_path), media_type='application/pdf')

