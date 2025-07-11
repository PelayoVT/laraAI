from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Usuario 
class UsuarioCreate(BaseModel):
    seudonimo: str
    password: str
    consentimiento_tratamiento: bool

class UsuarioOut(BaseModel):
    id: int
    seudonimo: str
    fecha_registro: datetime

    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    seudonimo: str
    password: str

# Conversacion 
class ConversacionOut(BaseModel):
    id: int
    user_id: int
    fecha_inicio: datetime
    fecha_inicio: datetime
    exportado_pdf: bool
    cerrada: bool

    class Config:
        orm_mode = True

class ConversacionCrear(BaseModel):
    usuario_id: int

class FinalizarConversacion(BaseModel):
    usuario_id: int

# Mensaje
class MensajeCreate(BaseModel):
    tipo: str  # "usuario" o "bot"
    contenido: str

class MensajeOut(BaseModel):
    id: int
    tipo: str
    contenido: str
    timestamp: datetime

    class Config:
        orm_mode = True
