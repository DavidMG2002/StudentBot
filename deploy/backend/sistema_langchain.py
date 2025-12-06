"""
Sistema Multiagente con LangChain
REQUISITO: Arquitectura donde varios agentes colaboren con roles claros

Agentes:
1. Agente Extractor: Lee documentos y crea chunks
2. Agente Buscador: Crea embeddings y busca similitudes
3. Agente Respondedor: Genera respuestas finales
"""
from typing import List, Dict
from langchain.agents import Tool
from agentes.extractor_langchain import AgenteExtractorLangChain
from agentes.buscador_langchain import AgenteBuscadorLangChain
from agentes.respondedor_langchain import AgenteRespondedorLangChain
from agentes.mejorador_respuestas import AgenteMejoradorGemini

class SistemaMultiagenteStudentBot:
    """
    Orquestador de Agentes usando LangChain
    
    Flujo de colaboración:
    Usuario → Agente Extractor → Agente Buscador → Agente Respondedor → Usuario
    """
    
    def __init__(self, carpeta_documentos="documentos", gemini_api_key=None):
        print("INICIALIZANDO SISTEMA MULTIAGENTE CON LANGCHAIN")
      
        
        # Inicializar agentes (cada uno con sus Tools)
        self.agente_extractor = AgenteExtractorLangChain(carpeta_documentos)
        self.agente_buscador = AgenteBuscadorLangChain()
        self.agente_respondedor = AgenteRespondedorLangChain()
        self.agente_gemini = AgenteMejoradorGemini(api_key=gemini_api_key)  # ← NUEVO
        
        # Estado del sistema
        self.documentos_cargados = False
        self.chunks = []
        
        # Crear tools del sistema (meta-level)
        self.system_tools = self._crear_system_tools()
        
        print(f"✓ Sistema inicializado con {len(self.system_tools)} herramientas")
        print(f"   • Agente Extractor: {len(self.agente_extractor.tools)} tools")
        print(f"   • Agente Buscador: {len(self.agente_buscador.tools)} tools")
        print(f"   • Agente Respondedor: {len(self.agente_respondedor.tools)} tools")
        print(f"   • Agente Gemini: {len(self.agente_gemini.tools)} tools")
        if self.agente_gemini.habilitado:
             print(f"Gemini Flash 2.0: ACTIVO")
        else:
             print(f"  |X|   Gemini: DESHABILITADO")
    
    def _crear_system_tools(self) -> List[Tool]:
        """Crea tools de coordinación del sistema"""
        return [
            Tool(
                name="cargar_documentos",
                func=self._cargar_documentos_tool,
                description="Ejecuta el flujo completo de carga de documentos"
            ),
            Tool(
                name="buscar_responder",
                func=self._buscar_responder_tool,
                description="Busca información y genera respuesta"
            ),
            Tool(
                name="estado_sistema",
                func=self._estado_sistema_tool,
                description="Obtiene el estado actual del sistema"
            )
        ]
    
    def _cargar_documentos_tool(self, tamano_chunk: str = "400") -> str:
        """Tool: Carga documentos usando los agentes"""
        try:
            tamano = int(tamano_chunk)
            self.cargar_documentos(tamano)
            return f"✓ Sistema listo: {len(self.chunks)} chunks creados"
        except Exception as e:
            return f"|X| Error: {str(e)}"
    
    def _buscar_responder_tool(self, pregunta: str) -> str:
        """Tool: Busca y responde usando los agentes"""
        try:
            respuesta = self.procesar_pregunta(pregunta)
            return respuesta
        except Exception as e:
            return f"|X| Error: {str(e)}"
    
    def _estado_sistema_tool(self, dummy: str = "") -> str:
        """Tool: Devuelve estado del sistema"""
        return f"{'✓' if self.documentos_cargados else '|X|'} Cargado: {len(self.chunks)} chunks"
    
    def cargar_documentos(self, tamano_chunk: int = 400) -> Dict:
        """
        Flujo de carga de documentos usando múltiples agentes
        
        Flujo:
        1. Agente Extractor → Lee archivos
        2. Agente Extractor → Crea chunks
        3. Agente Buscador → Crea embeddings
        4. Agente Buscador → Indexa en FAISS
        """
        
        # PASO 1: Agente Extractor lee documentos
        print("🔹 PASO 1: Agente Extractor leyendo documentos...")
        documentos = self.agente_extractor.leer_documentos()
        
        if not documentos:
            print("|X| No se encontraron documentos")
            return {'success': False, 'error': 'No hay documentos'}
        
        # PASO 2: Agente Extractor crea chunks
        print(f"\n🔹 PASO 2: Agente Extractor creando chunks...")
        self.chunks = self.agente_extractor.crear_chunks(tamano_chunk)
        
        if not self.chunks:
            print("|X| No se pudieron crear chunks")
            return {'success': False, 'error': 'Error en chunks'}
        
        # PASO 3: Agente Buscador crea base vectorial
        print(f"\n🔹 PASO 3: Agente Buscador indexando en FAISS...")
        self.agente_buscador.crear_base_vectorial(self.chunks)
        
        self.documentos_cargados = True
        
        print(f"\n{'='*60}")
        print("✓ FLUJO DE CARGA COMPLETADO")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'documentos': len(documentos),
            'chunks': len(self.chunks),
            'archivos': [f"{d['nombre']} ({d['tipo']})" for d in documentos]
        }
    
    def procesar_pregunta(self, pregunta: str, top_k: int = 3) -> str:
        """
        Flujo de procesamiento de pregunta usando múltiples agentes
        
        Flujo:
        1. Agente Buscador → Busca chunks relevantes
        2. Agente Respondedor → Genera respuesta
        """
        if not self.documentos_cargados:
            return "|X| Sistema no inicializado. Carga documentos primero."
        
        print(f"\n{'='*60}")
        print("🔍 INICIANDO FLUJO DE BÚSQUEDA MULTIAGENTE")
        print(f"{'='*60}\n")
        
        # PASO 1: Agente Buscador encuentra chunks relevantes
        print("🔹 PASO 1: Agente Buscador buscando información...")
        chunks_relevantes = self.agente_buscador.buscar_relevantes(pregunta, top_k)
        
        # PASO 2: Agente Respondedor genera respuesta
        print(f"\n🔹 PASO 2: Agente Respondedor generando respuesta...")
        respuesta = self.agente_respondedor.generar_respuesta_precisa(pregunta, chunks_relevantes)
        
        print(f"\n{'='*60}")
        print("✓ FLUJO DE BÚSQUEDA COMPLETADO")
        print(f"{'='*60}\n")
        
        return respuesta
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        if not self.documentos_cargados:
            return {
                'listo': False,
                'documentos': 0,
                'chunks': 0
            }
        
        tipos = {}
        for chunk in self.chunks:
            tipo = chunk.get('tipo', 'TXT')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        return {
            'listo': True,
            'documentos': len(self.agente_extractor.documentos),
            'chunks': len(self.chunks),
            'tipos': tipos,
            'agentes_activos': 3
        }
    
    def describir_arquitectura(self):
        """Describe la arquitectura multiagente"""
        print("🏗️  ARQUITECTURA MULTIAGENTE LANGCHAIN")
        print("""
┌─────────────────────────────────────────────────────┐
│           USUARIO (Frontend/API)                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│      SISTEMA ORQUESTADOR (LangChain)                │
│  • Coordina flujos entre agentes                    │
│  • Gestiona estado del sistema                      │
│  • Expone tools de alto nivel                       │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┐
        ▼                     ▼              ▼
┌───────────────┐    ┌───────────────┐    ┌────────────────┐
│ AGENTE 1      │    │ AGENTE 2      │    │ AGENTE 3       │
│ EXTRACTOR     │───▶│ BUSCADOR      │───▶│ RESPONDEDOR    │
│               │    │               │    │                │
│ ROL:          │    │ ROL:          │    │ ROL:           │
│ • Leer TXT    │    │ • Embeddings  │    │ • Generar      │
│ • Leer PDF    │    │ • FAISS       │    │   respuestas   │
│ • Aplicar OCR │    │ • Similitud   │    │ • Indicar      │
│ • Crear chunks│    │ • Reranking   │    │   confianza    │
│               │    │               │    │                │
│ TOOLS (4):    │    │ TOOLS (4):    │    │ TOOLS (3):     │
│ • leer_txt    │    │ • crear_emb   │    │ • generar_resp │
│ • leer_pdf    │    │ • buscar_sim  │    │ • extraer_rel  │
│ • aplicar_ocr │    │ • calc_simil  │    │ • calc_conf    │
│ • listar      │    │ • expandir    │    │                │
└───────────────┘    └───────────────┘    └────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌────────────┐        ┌────────────┐        ┌────────────┐
│ PyPDF2     │        │ Sentence   │        │ Templates  │
│ Tesseract  │        │ Transform  │        │ Formateo   │
│ (OCR)      │        │ FAISS      │        │            │
└────────────┘        └────────────┘        └────────────┘

FLUJO DE DATOS:
1. Usuario carga documentos
2. Extractor lee y segmenta (chunks)
3. Buscador crea embeddings e indexa
4. Usuario hace pregunta
5. Buscador encuentra chunks similares (coseno)
6. Respondedor genera respuesta con confianza
7. Usuario recibe respuesta estructurada
        """)
        


# Función helper para usar en backend
def crear_sistema(carpeta="documentos"):
    """
    Crea e inicializa el sistema multiagente
    Para usar en backend.py
    """
    return SistemaMultiagenteStudentBot(carpeta)