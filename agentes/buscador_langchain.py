"""
Agente 2: Buscador con LangChain
REQUISITO: Usar LangChain Tools para búsqueda vectorial
"""
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
from langchain.agents import Tool
from langchain.tools import BaseTool


class AgenteBuscadorLangChain:
    """
    Agente de Búsqueda implementado con LangChain
    Rol: Crear embeddings, indexar en FAISS y buscar chunks relevantes
    """
    
    def __init__(self, modelo_nombre='paraphrase-multilingual-MiniLM-L12-v2'):
        print("🤖 Agente Buscador LangChain: Cargando modelo...")
        
        try:
            self.modelo = SentenceTransformer(modelo_nombre)
            print(f"   ✅ Modelo: {modelo_nombre}")
        except:
            print("   ⚠️  Modelo multilingüe no disponible, usando fallback...")
            self.modelo = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        self.index = None
        self.chunks = []
        self.tools = self._crear_tools()
        
        print(f"   🔧 Tools: {len(self.tools)}")
    
    def _crear_tools(self) -> List[Tool]:
        """Crea las herramientas (tools) del agente"""
        return [
            Tool(
                name="crear_embeddings",
                func=self._crear_embeddings_tool,
                description="Crea embeddings vectoriales para un texto"
            ),
            Tool(
                name="buscar_similar",
                func=self._buscar_similar_tool,
                description="Busca textos similares usando similitud de coseno"
            ),
            Tool(
                name="calcular_similitud",
                func=self._calcular_similitud_tool,
                description="Calcula la similitud entre dos textos"
            ),
            Tool(
                name="expandir_consulta",
                func=self.expandir_consulta,
                description="Optimiza una consulta eliminando palabras vacías"
            )
        ]
    
    def _crear_embeddings_tool(self, texto: str) -> str:
        """Tool: Crea embedding de un texto"""
        try:
            embedding = self.modelo.encode([texto])
            return f"✅ Embedding creado: dimensión {embedding.shape[1]}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _buscar_similar_tool(self, consulta: str) -> str:
        """Tool: Busca textos similares"""
        if self.index is None:
            return "❌ Base vectorial no inicializada"
        
        resultados = self.buscar_relevantes(consulta, top_k=3)
        return f"✅ {len(resultados)} resultados encontrados"
    
    def _calcular_similitud_tool(self, textos: str) -> str:
        """Tool: Calcula similitud entre dos textos (separados por '|||')"""
        try:
            partes = textos.split('|||')
            if len(partes) != 2:
                return "❌ Formato: texto1|||texto2"
            
            emb1 = self.modelo.encode([partes[0]])
            emb2 = self.modelo.encode([partes[1]])
            
            # Normalizar y calcular similitud coseno
            faiss.normalize_L2(emb1.astype('float32'))
            faiss.normalize_L2(emb2.astype('float32'))
            similitud = np.dot(emb1[0], emb2[0])
            
            return f"✅ Similitud: {similitud:.2%}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def expandir_consulta(self, pregunta: str) -> str:
        """Tool: Expande y optimiza una consulta"""
        palabras_vacias = ['qué', 'cuál', 'cómo', 'dónde', 'cuándo', 'por qué', 
                          'es', 'son', 'está', 'están', 'el', 'la', 'los', 'las',
                          'un', 'una', 'unos', 'unas', 'de', 'del']
        
        palabras = pregunta.lower().split()
        palabras_importantes = [p for p in palabras if p not in palabras_vacias and len(p) > 2]
        
        consulta_expandida = ' '.join(palabras_importantes)
        print(f"   🔍 Consulta optimizada: '{consulta_expandida}'")
        
        return consulta_expandida
    
    def crear_base_vectorial(self, chunks: List[Dict]):
        """
        Crea la base vectorial FAISS usando los chunks
        Implementa el requisito de "base de datos vectorial"
        """
        print("🧮 Agente Buscador: Creando base vectorial FAISS...")
        
        if not chunks:
            print("⚠️  No hay chunks para procesar")
            return
        
        self.chunks = chunks
        textos = [c['texto'] for c in chunks]
        
        print(f"   📊 Procesando {len(textos)} chunks...")
        
        # Crear embeddings (requisito: embeddings y similitud)
        embeddings = self.modelo.encode(
            textos, 
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        embeddings = embeddings.astype('float32')
        
        # Normalizar para similitud de coseno (requisito: similitud)
        faiss.normalize_L2(embeddings)
        
        # Crear índice FAISS (requisito: base de datos vectorial)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product = coseno normalizado
        self.index.add(embeddings)
        
        # Estadísticas
        tipos = {}
        for chunk in chunks:
            tipo = chunk.get('tipo', 'TXT')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        print(f"✅ Base vectorial FAISS creada con {len(chunks)} vectores")
        print(f"   📈 Distribución: {', '.join([f'{k}: {v}' for k, v in tipos.items()])}")
        print(f"   🎯 Similitud: Coseno (Inner Product)")
        print(f"   📐 Dimensión: {dimension}")
    
    def calcular_relevancia_keywords(self, pregunta: str, chunk_texto: str) -> float:
        """Calcula relevancia basada en keywords"""
        pregunta_lower = pregunta.lower()
        chunk_lower = chunk_texto.lower()
        
        palabras_vacias = ['qué', 'cuál', 'cómo', 'dónde', 'cuándo', 'por', 'es', 'son', 
                          'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en']
        
        keywords = [p for p in pregunta_lower.split() 
                   if p not in palabras_vacias and len(p) > 3]
        
        matches = sum(1 for kw in keywords if kw in chunk_lower)
        
        return matches / len(keywords) if keywords else 0
    
    def buscar_relevantes(self, pregunta: str, top_k: int = 5) -> List[Dict]:
        """
        Busca los chunks más similares usando similitud de coseno
        Implementa requisito: "comparar textos usando similitud del coseno"
        """
        print(f"🔎 Agente Buscador: Buscando para '{pregunta[:50]}...'")
        
        if self.index is None or len(self.chunks) == 0:
            print("⚠️  Base vectorial no inicializada")
            return []
        
        # Expansión de consulta (usa Tool)
        consulta_expandida = self.expandir_consulta(pregunta)
        
        # Crear embedding de la pregunta
        pregunta_embedding = self.modelo.encode([consulta_expandida])
        pregunta_embedding = pregunta_embedding.astype('float32')
        
        # Normalizar
        faiss.normalize_L2(pregunta_embedding)
        
        # Buscar con FAISS (similitud de coseno)
        k_busqueda = min(top_k * 3, len(self.chunks))
        similitudes, indices = self.index.search(pregunta_embedding, k_busqueda)
        
        # Reranking con keywords
        resultados_con_score = []
        
        for i, idx in enumerate(indices[0]):
            chunk = self.chunks[idx].copy()
            
            # Score semántico (coseno)
            score_semantico = float(similitudes[0][i])
            
            # Score de keywords
            score_keywords = self.calcular_relevancia_keywords(pregunta, chunk['texto'])
            
            # Score combinado
            score_final = (score_semantico * 0.7) + (score_keywords * 0.3)
            
            chunk['score_semantico'] = score_semantico
            chunk['score_keywords'] = score_keywords
            chunk['relevancia'] = score_final
            
            resultados_con_score.append(chunk)
        
        # Ordenar por score
        resultados_con_score.sort(key=lambda x: x['relevancia'], reverse=True)
        
        # Filtrar por umbral
        umbral = 0.4
        resultados_filtrados = [r for r in resultados_con_score if r['relevancia'] >= umbral]
        
        if not resultados_filtrados:
            resultados_filtrados = resultados_con_score[:top_k]
        
        resultados_finales = resultados_filtrados[:top_k]
        
        print(f"✅ {len(resultados_finales)} chunks relevantes encontrados")
        for i, r in enumerate(resultados_finales, 1):
            print(f"   {i}. {r['fuente']} - Score: {r['relevancia']:.3f} "
                  f"(Sem: {r['score_semantico']:.3f}, KW: {r['score_keywords']:.3f})")
        
        return resultados_finales