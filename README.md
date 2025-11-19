🎓 StudentBot

Sistema Multiagente de Análisis Inteligente de Documentos con LangChain, FAISS y Gemini Flash 2.0

StudentBot es un asistente avanzado capaz de leer documentos TXT y PDF (incluidos escaneados), convertirlos en conocimiento estructurado y responder preguntas utilizando búsqueda semántica y modelos de IA generativa.

¿Qué es StudentBot?

StudentBot es un sistema inteligente que:

📄 Lee y procesa documentos TXT y PDF

🔍 Texto extra de PDF escaneado mediante OCR

🧠 Construye una base de conocimiento vectorial con FAISS

🔎 Realiza búsqueda semántica con incrustaciones multilingües

🤖 Genera respuestas avanzadas usando Gemini Flash 2.0

🧩 Utiliza una arquitectura multiagente optimizada con LangChain

🧩 Arquitectura Multiagente

El sistema está compuesto por 4 agentes especializados :

1️⃣ Agente Extractor

Lee documentos, realiza OCR y genera fragmentos inteligentes.

2️⃣ Agente Buscador

Crea incrustaciones y ejecuta búsquedas por similitud de coseno usando FAISS.

3️⃣ Agente Respondedor

Genera respuestas con puntuación de confianza y citas.

4️⃣ Agente Mejorador (Géminis)

Reescribe y optimiza respuestas para conversación natural.

📦 Requisitos previos

Python 3.10+

Librería pepita

(Opcional) Tesseract OCR para archivos PDF escaneados

(Opcional) Clave API de Google Gemini

⚙️ Instalación
1. Clonar el repositorio

git clone <tu-repo>
cd studentbot

2. Crear entorno virtual

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

3. Instalar dependencias

pip install -r requirements.txt

4. (Opcional) Instalar Tesseract

Windows:
Descargar desde:
https://github.com/UB-Mannheim/tesseract/wiki

Agregar al PATH.

Linux:

sudo apt-get install tesseract-ocr tesseract-ocr-spa

Impermeable:

brew install tesseract tesseract-lang

5. (Opcional) Configurar Géminis

Crear .enven la raíz:

GEMINI_API_KEY=tu_api_key_aqui

Obtener clave API en:
https://makersuite.google.com/app/apikey

📖 Uso del Sistema
🔌 Modo 1: API REST (Backend)

Iniciar servidor

python backend_langchain.py

Disponible en: http://localhost:5000

Puntos de conexión disponibles

➤ Cargar documentos

POST /api/cargar
{
  "carpeta": "documentos",
  "tamano_chunk": 400,
  "gemini_api_key": "opcional"
}

➤ Hacer pregunta

POST /api/preguntar
{
  "pregunta": "¿Qué es el emprendimiento?",
  "top_k": 3,
  "usar_gemini": true
}

➤ Estado del sistema

POST /api/resumen
{
  "documento": "nombre_documento.pdf"
}

🌐 Modo 2: Interfaz Web

cd frontend
python -m http.server 8000

Luego abrir en otro:

http://localhost:8000

🐍 Modo 3: Script Directo


from sistema_langchain import SistemaMultiagenteStudentBot

sistema = SistemaMultiagenteStudentBot(
    carpeta_documentos="documentos",
    gemini_api_key="tu_key_opcional"
)

resultado = sistema.cargar_documentos(tamano_chunk=400)
print(f"✓ {resultado['chunks']} chunks creados")

respuesta = sistema.procesar_pregunta("¿Qué es el emprendimiento?")
print(respuesta)

📁 Estructura del Proyecto

studentbot/
├── agentes/
│   ├── extractor_langchain.py
│   ├── buscador_langchain.py
│   ├── respondedor_langchain.py
│   └── mejorador_respuestas.py
├── documentos/
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── sistema_langchain.py
├── backend_langchain.py
├── config.py
├── requirements.txt
└── README.md

Configuración avanzada

Editar config.pypara:

MODELO_EMBEDDINGS

TAMANO_CHUNK_DEFECTO

UMBRAL_RELEVANCIA

TOP_K_DEFECTO

Pesos: PESO_SEMANTICO,PESO_KEYWORDS

🎨 Características Destacadas
📄 Procesamiento de Documentos

Soporte para TXT y PDF (nativo + OCR)

Respeto por párrafos y estructura

Metadatos del origen

🔍 Búsqueda Inteligente

Incrustaciones multilingües

FAISS + similitud de coseno

Re-rankeado por palabras clave

Expansión automática de consultas

🧠 Respuestas Inteligentes

Nivel de confianza: Muy Alta / Alta / Media / Baja

Citas y porcentajes de relevancia

Resúmenes ejecutivos

🤖 Integración con IA Generativa

Gemini Flash 2.0 para respuestas naturales

Modo conversacional

Mejora lingüística

🛠️Solución de Problemas

❌ OCR no disponible

pip install pytesseract pdf2image Pillow

Revisar la instalación de Tesseract.

❌ FAISS no encontrado

pip install faiss-cpu

❌ Error con la API de Gemini

Verificar clave API

Revisar variable de entorno

El sistema funciona sin Géminis.

🧪 Ejemplo Completo

Colocar PDF/TXT en/documentos/

Iniciar backend:

python backend_langchain.py


Cargar documentos

Interrogador:

¿Qué tipos de emprendimiento existen?


Recibir respuesta con fuentes y nivel de confianza

🤝 Contribuciones

Para sugerencias o errores abre un problema en el repositorio.
Las contribuciones son bienvenidas.