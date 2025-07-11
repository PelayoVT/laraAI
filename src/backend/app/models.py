from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    seudonimo = Column(String, nullable=False)
    password = Column(String, nullable=False)
    consentimiento_tratamiento = Column(Boolean, default=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    conversaciones = relationship("Conversation", back_populates="usuario")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    cerrada = Column(Boolean, default=False)
    exportado_pdf = Column(Boolean, default=False)

    usuario = relationship("User", back_populates="conversaciones")
    mensajes = relationship("Message", back_populates="conversacion")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    tipo = Column(String, nullable=False)  # "usuario" o "bot"
    contenido = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    conversacion = relationship("Conversation", back_populates="mensajes")
