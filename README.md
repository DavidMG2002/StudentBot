# StudentBot – Sistema Multi-Agente de Análisis de Documentos

Sistema inteligente para procesamiento y análisis de documentos (TXT y PDF) mediante agentes especializados, búsqueda vectorial, OCR y generación de respuestas con IA.

---

## Pila Tecnológica

### Backend:

- Python 3.10+
- LangChain (Gestión de agentes y cadenas)
- FAISS (Vectorial base)
- Google Gemini Flash 2.0 (Mejora de respuestas)
- Flask (API REST)
- OCR Tesseract (opcional)
- pepita (Marco adicional utilizado en el proyecto)

### Interfaz:

- HTML, CSS, JavaScript
- Servidor simple con http.server (modo local)

---

## Características

- 4 agentes especializados (Extractor, Buscador, Respondedor, Mejorador)
- Procesamiento de documentos TXT y PDF (incluye OCR)
- Búsqueda semántica mediante incrustaciones multilingües
- Sistema de puntuación y nivel de confianza en respuestas
- Mejoras de lenguaje natural con Gemini Flash 2.0
- Arquitectura modular y escalable
- API REST + Interfaz Web Simple
- Soporte para análisis conversacional

---

## Arquitectura Multi-Agente

### 1. Agente Extractor

- Lee documentos TXT y PDF
- Aplica OCR en PDFs escaneados
- Genera trozos inteligentes
- Extrae metadatos útiles

### 2. Agente Buscador

- Convierte los trozos en incrustaciones
- Almacena vectores en FAISS
- Calcula similitud de coseno
- Reordena resultados por palabras clave

### 3. Agente Respondedor

- Genera respuestas contextuales
- Añade nivel de confianza (Muy Alta, Alta, Media, Baja)
- Incluye citas y fuentes del documento

### 4. Agente Mejorador (Gemini)

- Reescribe las respuestas
- Mejora la claridad, coherencia y naturalidad
- Genera resúmenes ejecutivos y explicaciones más limpias

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd studentbot
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. (Opcional) Instalar Tesseract para OCR

**Windows:**
```
https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

**Mac:**
```bash
brew install tesseract tesseract-lang
```

### 5. Configurar clave de Gemini (opcional)

Crear archivo `.env`:

```
GEMINI_API_KEY=tu_api_key
```

---

## Uso

### Modo API REST

Iniciar el backend:

```bash
python backend_langchain.py
```

El servidor estará disponible en: **http://localhost:5000**

#### Cargar documentos

```http
POST /api/cargar
{
  "carpeta": "documentos",
  "tamano_chunk": 400
}
```

#### Hacer una pregunta

```http
POST /api/preguntar
{
  "pregunta": "¿Qué es el emprendimiento?",
  "top_k": 3,
  "usar_gemini": true
}
```

#### Estado del sistema

```http
POST /api/resumen
{
  "documento": "archivo.pdf"
}
```

### Modo Interfaz Web

```bash
cd frontend
python -m http.server 8000
```

Abrir en: **http://localhost:8000**

### Modo Script

```python
from sistema_langchain import SistemaMultiagenteStudentBot

sistema = SistemaMultiagenteStudentBot(
    carpeta_documentos="documentos",
    gemini_api_key="tu_key"
)

resultado = sistema.cargar_documentos(tamano_chunk=400)
print(resultado)

respuesta = sistema.procesar_pregunta("¿Qué es el emprendimiento?")
print(respuesta)
```

---

## Estructura del Proyecto

```
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
```

---

## Solución de Problemas

### OCR no disponible

```bash
pip install pytesseract pdf2image Pillow
```

### FAISS no instalado

```bash
pip install faiss-cpu
```

### Error con Gemini

- Revisar variable `GEMINI_API_KEY`
- El sistema puede funcionar sin Gemini

---

## Contribuciones

Para sugerencias o mejoras, abra un issue en el repositorio.