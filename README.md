# LaraAI - Chatbot de Apoyo Psicológico

LaraAI es un asistente virtual diseñado para ayudar a los usuarios a explorar sus emociones y detectar signos de ansiedad. Este proyecto ha sido desarrollado como Trabajo de Fin de Grado en el marco del programa OneHealth.

## 🎓 Autor

**Pelayo Vázquez**
Estudiante de 4º curso del Grado en Ingeniería Informática
Universidad Europea de Madrid (UEM)
Curso 2024/2025

## 🌐 Proyecto OneHealth

OneHealth es una iniciativa que promueve soluciones tecnológicas al servicio del bienestar global, integrando salud humana, animal y medioambiental. En este contexto, LaraAI se centra en la salud mental, permitiendo una detección temprana de la ansiedad mediante un chatbot entrenado con modelos de lenguaje.

## 🚀 Tecnologías empleadas

* **Frontend**: Angular 17
* **Backend**: FastAPI (Python 3.12)
* **Base de datos**: SQLite (SQLAlchemy ORM)
* **Modelo de lenguaje**: Mistral-7B con LoRA (fine-tuning)
* **PDF export**: ReportLab
* **Otros**: HTML, CSS, Bootstrap, TypeScript

## 🪧 Instalación y despliegue

### 1. Clonar el repositorio

```bash
git clone https://github.com/PelayoVT/laraAI.git
cd laraAI
```

### 2. Backend (FastAPI)

```bash
cd src/backend
python -m venv env
source env/bin/activate  # o env\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend (Angular)

```bash
cd src/frontend
npm install
ng serve
```

Accede a la app desde: [http://localhost:4200](http://localhost:4200)

## 🔐 Funcionalidades

* Sistema conversacional especializado en ansiedad
* Registro y login con seudónimo
* Aceptación del consentimiento informado
* Creación y cierre de conversaciones
* Persistencia de sesiones
* Exportación a PDF de conversaciones cerradas
* Bloqueo de interacción cuando la conversación ha finalizado

## 📊 Estructura del proyecto

```
TFG/
├── .gitignore
├── README.md
├── requirements.txt
├── datasets/                     
├── model/                
│   ├── modelo_clinico_lora/  
│   └── modelo_lora/    
└── src/
    ├── backend/          
    ├── frontend/         
    └── aitraining/                       
```

## ✉️ Contacto

Para cualquier duda o propuesta:

* Email: [pelayo.pvt@gmail.com](mailto:pelayo.pvt@gmail.com)
* GitHub: [@PelayoVT](https://github.com/PelayoVT)

## ✅ Licencia

Este proyecto está licenciado bajo **MIT License**. Consulta el archivo `LICENSE` para más detalles.
