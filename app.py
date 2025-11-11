"""
DocuBot - Asistente Inteligente de Documentos
Aplicación principal con interfaz Streamlit
"""
import streamlit as st
import sys
import os

# Agregar carpeta agentes al path
sys.path.append(os.path.dirname(__file__))

from agentes.extractor import AgenteExtractor
from agentes.buscador import AgenteBuscador
from agentes.respondedor import AgenteRespondedor

# Configuración de la página
st.set_page_config(
    page_title="DocuBot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 DocuBot - Asistente Inteligente de Documentos")
st.markdown("*Sistema multiagente para consultar documentos usando IA*")

# Estado de sesión para mantener el sistema cargado
if 'sistema_listo' not in st.session_state:
    st.session_state.sistema_listo = False
    st.session_state.agente_extractor = None
    st.session_state.agente_buscador = None
    st.session_state.agente_respondedor = None

# Sidebar para cargar documentos
with st.sidebar:
    st.header("⚙️ Configuración")
    
    carpeta = st.text_input("Carpeta de documentos", "documentos")
    tamano_chunk = st.slider("Tamaño de chunks", 100, 500, 300)
    top_k = st.slider("Resultados a buscar", 1, 5, 3)
    
    if st.button("🚀 Cargar Documentos", type="primary"):
        with st.spinner("Cargando sistema..."):
            # Inicializar agentes
            st.session_state.agente_extractor = AgenteExtractor(carpeta)
            st.session_state.agente_buscador = AgenteBuscador()
            st.session_state.agente_respondedor = AgenteRespondedor()
            
            # Proceso de carga
            documentos = st.session_state.agente_extractor.leer_documentos()
            
            if documentos:
                chunks = st.session_state.agente_extractor.crear_chunks(tamano_chunk)
                st.session_state.agente_buscador.crear_base_vectorial(chunks)
                st.session_state.sistema_listo = True
                st.success(f"✅ Sistema listo! {len(documentos)} documentos cargados")
            else:
                st.error("❌ No se encontraron documentos .txt")
    
    st.markdown("---")
    st.markdown("### 📖 Instrucciones")
    st.markdown("""
    1. Coloca archivos .txt en la carpeta `documentos/`
    2. Haz clic en 'Cargar Documentos'
    3. Escribe tu pregunta abajo
    """)

# Área principal
if st.session_state.sistema_listo:
    st.success("✅ Sistema activo - Puedes hacer preguntas")
    
    # Input de pregunta
    pregunta = st.text_input(
        "🤔 Escribe tu pregunta:",
        placeholder="¿Qué información contienen los documentos sobre...?"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        buscar = st.button("🔍 Buscar", type="primary")
    
    if buscar and pregunta:
        with st.spinner("Procesando pregunta..."):
            # Flujo multiagente
            st.markdown("### 🔄 Proceso de los Agentes")
            
            # Agente Buscador
            with st.expander("🤖 Agente Buscador - Resultados"):
                chunks = st.session_state.agente_buscador.buscar_relevantes(
                    pregunta, top_k
                )
                for i, chunk in enumerate(chunks, 1):
                    st.markdown(f"**Resultado {i}** ({chunk['fuente']}):")
                    st.text(chunk['texto'][:200] + "...")
            
            # Agente Respondedor
            respuesta = st.session_state.agente_respondedor.generar_respuesta(
                pregunta, chunks
            )
            
            st.markdown("### 💬 Respuesta Final")
            st.markdown(respuesta)
else:
    st.info("👈 Carga los documentos desde el panel lateral para comenzar")
    
    # Ejemplo de documentos
    st.markdown("### 📝 Ejemplo de documento")
    st.code("""
# documento1.txt
Python es un lenguaje de programación de alto nivel.
Es muy usado en ciencia de datos e inteligencia artificial.
Fue creado por Guido van Rossum en 1991.
    """, language="text")
    
    st.markdown("### 🏗️ Arquitectura del Sistema")
    st.markdown("""
    **Flujo Multiagente:**
    
    1. **Agente Extractor** → Lee y segmenta documentos
    2. **Agente Buscador** → Busca información relevante usando embeddings
    3. **Agente Respondedor** → Genera la respuesta final
    
    **Tecnologías:**
    - Embeddings: Sentence Transformers
    - Base vectorial: FAISS
    - Similitud: Distancia euclidiana (L2)
    """)

# Footer
st.markdown("---")
st.markdown("*Proyecto académico - Tecnología en Desarrollo de Software*")