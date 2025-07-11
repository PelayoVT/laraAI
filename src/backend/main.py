from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
from sqlalchemy.orm import Session
from pathlib import Path
import torch

from app.routes import inicio, conversacion
from app.database import Base, engine, SessionLocal
from app import models
from app.utils import pdf

# === INICIALIZACIÓN ===
app = FastAPI(title="Chatbot Clínico Ansiedad")

Base.metadata.create_all(bind=engine)
app.include_router(inicio.router)
app.include_router(inicio.router)
app.include_router(conversacion.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargamos el modelo
lora_path = Path(__file__).resolve().parents[2] / "model_outputs" / "modelo_clinico_lora"
base_model = "mistralai/Mistral-7B-v0.3"

tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16, device_map="auto")

peft_config = PeftConfig.from_pretrained(str(lora_path))
model = PeftModel.from_pretrained(model, str(lora_path), config=peft_config)
model.eval()

# Formato del input
class Consulta(BaseModel):
    mensaje: str
    id_conversacion: int

# LLamada al modelo
def generar_respuesta(mensaje_usuario: str, max_tokens=256):
    prompt = f"<|user|>\n{mensaje_usuario.strip()}\n<|assistant|>\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    output = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    if "<|assistant|>" in decoded:
        after = decoded.split("<|assistant|>", 1)[-1]
        return after.split("<|user|>")[0].strip()
    return decoded.strip()


# Enpoint del chat
@app.post("/chat")
def conversar(entrada: Consulta, db: Session = Depends(get_db)):
    conversacion = db.query(models.Conversation).filter(models.Conversation.id == entrada.id_conversacion).first()
    if not conversacion:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    if conversacion.cerrada:
        raise HTTPException(status_code=400, detail="Esta conversación ya fue finalizada")

    # Guardar mensaje del usuario
    mensaje_usuario = models.Message(
        conversation_id=entrada.id_conversacion,
        tipo="usuario",
        contenido=entrada.mensaje
    )
    db.add(mensaje_usuario)
    db.commit()

    # Generar respuesta del bot
    respuesta = generar_respuesta(entrada.mensaje)

    # Guardar mensaje del bot
    mensaje_bot = models.Message(
        conversation_id=entrada.id_conversacion,
        tipo="bot",
        contenido=respuesta
    )
    db.add(mensaje_bot)
    db.commit()

    return {"respuesta": respuesta}
