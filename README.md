# StudentBot — Asistente Inteligente de Documentos

Proyecto multiagente que permite cargar, indexar y consultar documentos (TXT / PDF) usando LangChain, FAISS y un módulo opcional de mejora de respuestas con Gemini.

## Contenido del repositorio
- [backend_langchain.py](backend_langchain.py) — API REST y orquestador del backend  
- [sistema_langchain.py](sistema_langchain.py) — Orquestador principal: [`sistema_langchain.SistemaMultiagenteDocuBot`](sistema_langchain.py)  
- Agentes:
  - [`agentes.extractor_langchain.AgenteExtractorLangChain`](agentes/extractor_langchain.py) — Lectura y creación de chunks  
  - [`agentes.buscador_langchain.AgenteBuscadorLangChain`](agentes/buscador_langchain.py) — Embeddings, FAISS y búsqueda  
  - [`agentes.respondedor_langchain.AgenteRespondedorLangChain`](agentes/respondedor_langchain.py) — Generación de respuestas y cálculo de confianza  
  - [`agentes.mejorador_respuestas.AgenteMejoradorGemini`](agentes/mejorador_respuestas.py) — Mejora las respuestas con Gemini (opcional)  
- Frontend estático: [frontend/index.html](frontend/index.html), [frontend/script.js](frontend/script.js), [frontend/style.css](frontend/style.css)  
- Configuración: [config.py](config.py), [.env](.env)  
- Tests / utilidades: [test_langchain.py](test_langchain.py)  
- Interfaz Streamlit: [app.py](app.py)  
- Dependencias: [requirements.txt](requirements.txt)

---

## Requisitos
- Python 3.8+  
- Recomendado: crear un entorno virtual (venv)
- Instalar dependencias:
```sh
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

(Archivo: [requirements.txt](requirements.txt))

---

## Configuración (Gemini API)
- Copia `.env` si es necesario y añade tu API key de Gemini:
  - Edita [.env](.env) y establece `GEMINI_API_KEY=tu_key` o exporta la variable de entorno.
- Si no se proporciona key, el sistema funciona sin la mejora Gemini (modo degradado).

---

## Ejecutar el backend (API)
1. Iniciar la API REST (Flask):
```sh
python backend_langchain.py
```
- La API queda disponible en: http://localhost:5000  
- Endpoints principales:
  - GET /api/status → estado del sistema
  - POST /api/cargar → carga e indexa documentos
  - POST /api/preguntar → hacer consultas sobre documentos
  - POST /api/resumen → generar resumen (requiere Gemini)

(Backend implementado en [backend_langchain.py](backend_langchain.py))

Ejemplo CURL:
```sh
curl http://localhost:5000/api/status
```

Cargar documentos (ejemplo):
```sh
curl -X POST http://localhost:5000/api/cargar \
  -H "Content-Type: application/json" \
  -d '{"carpeta":"documentos","tamano_chunk":400}'
```

Preguntar:
```sh
curl -X POST http://localhost:5000/api/preguntar \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"¿De qué tratan los documentos?","top_k":3,"usar_gemini":true}'
```

---

## Frontend (interfaz rápida)
- Abrir [frontend/index.html](frontend/index.html) en el navegador.
- El frontend envía peticiones a la API en http://localhost:5000/api (ver [frontend/script.js](frontend/script.js)).

Alternativa UI con Streamlit:
```sh
streamlit run app.py
```
(Interfaz en [app.py](app.py))

---

## Flujo de uso (resumen)
1. Coloca archivos .txt / .pdf en la carpeta `documentos/`.
2. Inicia el backend: `python backend_langchain.py`.
3. Desde el frontend (o curl), llama a `/api/cargar` para procesar e indexar los documentos.
4. Haz consultas con `/api/preguntar`. El flujo es:
   - [`agentes.buscador_langchain.AgenteBuscadorLangChain`](agentes/buscador_langchain.py) busca chunks relevantes.
   - [`agentes.respondedor_langchain.AgenteRespondedorLangChain`](agentes/respondedor_langchain.py) genera la respuesta base.
   - Opcional: [`agentes.mejorador_respuestas.AgenteMejoradorGemini`](agentes/mejorador_respuestas.py) mejora la respuesta si Gemini está habilitado.

El orquestador de alto nivel es [`sistema_langchain.SistemaMultiagenteDocuBot`](sistema_langchain.py).

---

## Pruebas
- Ejecuta la suite de comprobación:
```sh
python test_langchain.py
```
(Archivo: [test_langchain.py](test_langchain.py))

---

## Buenas prácticas y notas
- Limita el número de documentos grandes para evitar uso excesivo de memoria (ver [config.py](config.py)).  
- Si trabajas con PDFs escaneados, instala Tesseract y dependencias para habilitar OCR (se revisa en [`agentes.extractor_langchain.AgenteExtractorLangChain`](agentes/extractor_langchain.py)).  
- Para mejorar resultados en español, use el modelo multilingüe por defecto definido en [config.py](config.py).

---

## Resolución de problemas rápidos
- "Backend no disponible": asegúrate de ejecutar `python backend_langchain.py` y que el puerto 5000 esté libre.
- Errores con embeddings / FAISS: verifica que las dependencias de `sentence-transformers` y `faiss` se instalaron correctamente.
- Gemini no mejora respuestas: confirma que `GEMINI_API_KEY` está presente en [.env](.env) o en variables de entorno.

---

