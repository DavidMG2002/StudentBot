"""
Configuración del Sistema DocuBot
Ajusta estos parámetros para mejorar la precisión
"""

# ==========================================
# CONFIGURACIÓN DE EMBEDDINGS
# ==========================================

# Modelo de embeddings a usar
# Opciones (de más preciso a más rápido):
# 1. 'paraphrase-multilingual-MiniLM-L12-v2' - MEJOR para español (recomendado)
# 2. 'paraphrase-multilingual-mpnet-base-v2' - MUY PRECISO pero más lento
# 3. 'all-MiniLM-L6-v2' - Rápido, bueno para inglés
# 4. 'paraphrase-MiniLM-L6-v2' - Original, más rápido

MODELO_EMBEDDINGS = 'paraphrase-multilingual-MiniLM-L12-v2'

# Tamaño de batch para procesar embeddings
BATCH_SIZE = 32

# ==========================================
# CONFIGURACIÓN DE CHUNKS
# ==========================================

# Tamaño objetivo de chunks (en caracteres)
# Más pequeño = más preciso pero más fragmentado
# Más grande = más contexto pero puede ser menos preciso
TAMANO_CHUNK_DEFECTO = 400

# Usar chunks inteligentes (por párrafos) en lugar de arbitrarios
USAR_CHUNKS_INTELIGENTES = True

# Tamaño mínimo de chunk para considerar
TAMANO_MINIMO_CHUNK = 50

# ==========================================
# CONFIGURACIÓN DE BÚSQUEDA
# ==========================================

# Número de resultados a buscar por defecto
TOP_K_DEFECTO = 3

# Umbral de relevancia mínima (0.0 a 1.0)
# 0.0 = Acepta todo
# 0.5 = Solo resultados medianamente relevantes
# 0.8 = Solo resultados muy relevantes
UMBRAL_RELEVANCIA = 0.4

# Multiplicador para búsqueda inicial (para reranking)
# Busca K * MULTIPLICADOR resultados y luego los reordena
MULTIPLICADOR_BUSQUEDA = 3

# Usar expansión de consulta (elimina palabras vacías)
USAR_EXPANSION_CONSULTA = True

# Palabras vacías en español (se ignoran en búsqueda)
PALABRAS_VACIAS = {
    'qué', 'cuál', 'cómo', 'dónde', 'cuándo', 'por', 'qué', 'quién',
    'es', 'son', 'está', 'están', 'era', 'eran',
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'al', 'en', 'con', 'sin', 'sobre', 'para',
    'y', 'o', 'pero', 'si', 'no', 'ni', 'que',
    'me', 'te', 'se', 'nos', 'os',
    'mi', 'tu', 'su', 'nuestro', 'vuestro',
    'este', 'ese', 'aquel', 'esta', 'esa', 'aquella'
}

# ==========================================
# CONFIGURACIÓN DE SCORING
# ==========================================

# Peso del score semántico (0.0 a 1.0)
PESO_SEMANTICO = 0.7

# Peso del score de keywords (0.0 a 1.0)
# PESO_SEMANTICO + PESO_KEYWORDS debe sumar 1.0
PESO_KEYWORDS = 0.3

# ==========================================
# CONFIGURACIÓN DE RESPUESTAS
# ==========================================

# Número máximo de oraciones a extraer por chunk
MAX_ORACIONES_POR_CHUNK = 2

# Incluir indicador de confianza en respuestas
MOSTRAR_CONFIANZA = True

# Incluir barra de relevancia visual
MOSTRAR_BARRA_RELEVANCIA = True

# Tipo de respuesta por defecto
# 'precisa' - Respuesta optimizada (recomendado)
# 'simple' - Solo lo esencial
# 'detallada' - Análisis completo con todos los datos
TIPO_RESPUESTA_DEFECTO = 'precisa'

# ==========================================
# CONFIGURACIÓN DE CONTEXTO EXTENDIDO
# ==========================================

# Incluir chunks vecinos para mayor contexto
USAR_CONTEXTO_EXTENDIDO = False

# Número de chunks vecinos a incluir (antes y después)
NUMERO_CHUNKS_VECINOS = 1

# ==========================================
# CONFIGURACIÓN AVANZADA
# ==========================================

# Usar similitud de coseno en lugar de distancia euclidiana
# True = Más preciso (recomendado)
# False = Más rápido
USAR_SIMILITUD_COSENO = True

# Normalizar embeddings
NORMALIZAR_EMBEDDINGS = True

# Límite de documentos a procesar
LIMITE_DOCUMENTOS = 20

# Límite de caracteres por documento PDF
LIMITE_CHARS_PDF = 500000  # 500K caracteres

# ==========================================
# MENSAJES DEL SISTEMA
# ==========================================

MENSAJE_BIENVENIDA = """
¡Hola! Soy DocuBot, tu asistente inteligente de documentos.

Puedo leer y analizar archivos TXT y PDF.
Carga tus documentos y haré preguntas sobre su contenido.

✨ Ahora con MAYOR PRECISIÓN:
• Modelo multilingüe optimizado para español
• Búsqueda semántica avanzada
• Respuestas con indicador de confianza
• Chunks inteligentes que respetan párrafos
"""

MENSAJE_SIN_DOCUMENTOS = """
📂 No hay documentos cargados.

Para comenzar:
1. Coloca archivos .txt o .pdf en la carpeta 'documentos/'
2. Haz clic en "Cargar Documentos"
3. Espera a que se procesen
4. ¡Haz tu pregunta!
"""

MENSAJE_ERROR_BACKEND = """
❌ No se pudo conectar con el backend.

Asegúrate de que el servidor esté ejecutándose:
python backend.py
"""

# ==========================================
# CONFIGURACIÓN DE DEBUG
# ==========================================

# Mostrar información detallada en consola
DEBUG_MODE = True

# Mostrar scores de relevancia
MOSTRAR_SCORES = True

# Mostrar tiempo de procesamiento
MOSTRAR_TIEMPO = True