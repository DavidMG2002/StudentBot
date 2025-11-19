StudentBot 📚
Sistema multiagente de análisis de documentos que utiliza LangChain, FAISS y Gemini Flash 2.0 para responder preguntas sobre archivos TXT y PDF mediante búsqueda semántica avanzada.
 ¿Qué es StudentBot?
StudentBot es un asistente inteligente que:

Lee y procesa documentos TXT y PDF (incluye OCR para PDF escaneados)
Crea una base de conocimiento vectorial con FAISS
Responde preguntas usando búsqueda semántica con incrustaciones multilingües
Mejora respuestas con IA generativa (Gemini Flash 2.0)
Arquitectura multiagente con LangChain

Arquitectura Multiagente
El sistema está compuesto por 4 agentes especializados:

Agente Extractor : Lee documentos y crea trozos inteligentes
Agente Buscador : Genera incrustaciones y busca por similitud de coseno
Agente Respondedor : Genera respuestas con indicadores de confianza
Agente Mejorador (Gemini) : Transforma respuestas a lenguaje natural

 Requisitos previos

Python 3.10+
pepita
(Opcional) Tesseract OCR para archivos PDF escaneados
(Opcional) API Key de Google Gemini para respuestas mejoradas

 Instalación

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

4. (Opcional) Instalar Tesseract para OCR
Windows:

Descargar de: https://github.com/UB-Mannheim/tesseract/wiki
Agregar al PATH

Linux:

sudo apt-get install tesseract-ocr tesseract-ocr-spa

Impermeable:

brew install tesseract tesseract-lang

5. (Opcional) Configurar Géminis
Crear archivo .enven la raíz:

GEMINI_API_KEY=tu_api_key_aqui

Obtenga su clave API en: https://makersuite.google.com/app/apikey

📖 Uso
Modo 1: API REST (Backend)

Iniciar servidor

python backend_langchain.py

El servidor estará disponible enhttp://localhost:5000
Puntos de conexión disponibles

Cargar documentos:

POST /api/cargar
{
  "carpeta": "documentos",
  "tamano_chunk": 400,
  "gemini_api_key": "opcional"
}

Hacer pregunta:

POST /api/preguntar
{
  "pregunta": "¿Qué es el emprendimiento?",
  "top_k": 3,
  "usar_gemini": true
}

Estado del sistema:

POST /api/resumen
{
  "documento": "nombre_documento.pdf"
}

Modo 2: Interfaz Web (Frontend)
Iniciar frontend

cd frontend
# Abrir index.html en navegador
# O usar servidor local:
python -m http.server 8000

Modo 3: Script Directo

from sistema_langchain import SistemaMultiagenteStudentBot

# Crear sistema
sistema = SistemaMultiagenteStudentBot(
    carpeta_documentos="documentos",
    gemini_api_key="tu_key_opcional"
)

# Cargar documentos
resultado = sistema.cargar_documentos(tamano_chunk=400)
print(f"✓ {resultado['chunks']} chunks creados")

# Hacer pregunta
respuesta = sistema.procesar_pregunta("¿Qué es el emprendimiento?")
print(respuesta)
```

## 📁 Estructura del Proyecto
```
studentbot/
├── agentes/
│   ├── extractor_langchain.py      # Agente 1: Lectura de docs
│   ├── buscador_langchain.py       # Agente 2: Búsqueda vectorial
│   ├── respondedor_langchain.py    # Agente 3: Generación de respuestas
│   └── mejorador_respuestas.py     # Agente 4: Mejora con Gemini
├── documentos/                      # Carpeta para TXT y PDF
├── frontend/
│   ├── index.html                   # Interfaz web
│   ├── script.js                    # Lógica del cliente
│   └── style.css                    # Estilos
├── sistema_langchain.py             # Orquestador multiagente
├── backend_langchain.py             # API REST con Flask
├── config.py                        # Configuración del sistema
├── requirements.txt                 # Dependencias
└── README.md                        # Este archivo

 Configuración avanzada
Editar config.pypara:

Modelo de embeddings :MODELO_EMBEDDINGS
Tamaño de chunks :TAMANO_CHUNK_DEFECTO
Umbral de relevancia :UMBRAL_RELEVANCIA
Resultados Top-K :TOP_K_DEFECTO
Pesos de puntuación : PESO_SEMANTICO,PESO_KEYWORDS

🎨 Características

✅ Procesamiento de Documentos

TXT con codificación UTF-8
PDF nativos y escaneados (OCR)
Chunks inteligentes que respetan párrafos
Metadatos de fuente y método de extracción

✅ Búsqueda Inteligente

Incrustaciones multilingües optimizadas para español.
Similitud de coseno con FAISS
Reposicionamiento de palabras clave
Expansión automática de consultas

✅ Respuestas Contextualizadas

Indicadores de confianza (Muy Alta, Alta, Media, Baja)
Extracción de oraciones relevantes
Fuentes citadas con puntuaciones
Resúmenes ejecutivos

✅ Integración con IA Generativa

Gemini Flash 2.0 para respuestas naturales
Generación de resúmenes de documentos.
Modo conversacional con historial

Solución de Problemas
Error: "OCR no disponible"

pip install pytesseract pdf2image Pillow
# Instalar Tesseract (ver paso 4)

Error: "FAISS no encontrado"

pip install faiss-cpu

Error: "Error de la API de Gemini"

Verificar clave API.
Revisar variable de entornoGEMINI_API_KEY
El sistema funciona sin Gemini (respuestas base)

los documentos no se cargan

Verificar: documentos/existe
Los archivos deben ser .txt o .pdf
Revisar los límites de lectura

Ejemplo Completo

Coloca tus PDF/TXT en una carpetadocumentos/
Inicia backend:python backend_langchain.py
Interfaz de usuario de Abre:frontend/index.html
Haz clic en "Cargar mensajes"
Escribe pregunta: "¿Qué tipos de emprendimiento existen?"
Recibe respuesta con fuentes y nivel de confianza

🤝 Contribuciones
Para reportar errores o sugerir mejoras, abre un problema en el repositorio.