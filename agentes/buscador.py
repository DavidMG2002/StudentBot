"""
Agente 2: Buscador
Responsabilidad: Crear embeddings, guardarlos en FAISS y buscar chunks relevantes
MEJORAS DE PRECISIÓN:
- Usa modelo multilingüe (mejor para español)
- Reranking de resultados
- Filtrado por umbral de relevancia
- Expansión de consulta
"""
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re

class AgenteBuscador:
    def __init__(self, modelo_nombre='paraphrase-multilingual-MiniLM-L12-v2'):
        print("🤖 Agente Buscador: Cargando modelo de embeddings...")
        # MEJORA: Modelo MULTILINGÜE para mejor comprensión del español
        # Opciones:
        # - 'paraphrase-multilingual-MiniLM-L12-v2' (multilingüe, mejor español)
        # - 'paraphrase-MiniLM-L6-v2' (solo inglés, más rápido)
        # - 'all-MiniLM-L6-v2' (general, rápido)
        try:
            self.modelo = SentenceTransformer(modelo_nombre)
            print(f"   ✅ Modelo cargado: {modelo_nombre}")
        except:
            print("   ⚠️  Modelo multilingüe no disponible, usando fallback...")
            self.modelo = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        
        self.index = None
        self.chunks = []
        self.umbral_relevancia = 1.5  # Menor = más estricto
        
    def expandir_consulta(self, pregunta):
        """
        Expande la consulta con términos relacionados para mejor búsqueda
        """
        # Eliminar palabras de relleno que no aportan significado
        palabras_vacias = ['qué', 'cuál', 'cómo', 'dónde', 'cuándo', 'por qué', 
                          'es', 'son', 'está', 'están', 'el', 'la', 'los', 'las',
                          'un', 'una', 'unos', 'unas', 'de', 'del']
        
        palabras = pregunta.lower().split()
        palabras_importantes = [p for p in palabras if p not in palabras_vacias and len(p) > 2]
        
        # Reconstruir consulta enfocada
        consulta_expandida = ' '.join(palabras_importantes)
        
        print(f"   🔍 Consulta optimizada: '{consulta_expandida}'")
        
        return consulta_expandida
    
    def crear_base_vectorial(self, chunks):
        """Convierte chunks a embeddings y crea base FAISS"""
        print("🧮 Agente Buscador: Creando embeddings...")
        
        if not chunks:
            print("⚠️  No hay chunks para procesar")
            return
        
        self.chunks = chunks
        textos = [c['texto'] for c in chunks]
        
        print(f"   📊 Procesando {len(textos)} chunks...")
        
        # MEJORA: Usar batch_size para procesar más eficientemente
        embeddings = self.modelo.encode(
            textos, 
            show_progress_bar=True,
            batch_size=32,  # Procesar en lotes
            convert_to_numpy=True
        )
        embeddings = embeddings.astype('float32')
        
        # Normalizar embeddings para búsqueda por coseno (más preciso)
        # MEJORA: Similitud de coseno en lugar de distancia euclidiana
        faiss.normalize_L2(embeddings)
        
        # Crear índice FAISS con producto interno (coseno después de normalizar)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # IP = Inner Product (coseno)
        self.index.add(embeddings)
        
        # Estadísticas
        tipos = {}
        for chunk in chunks:
            tipo = chunk.get('tipo', 'TXT')
            tipos[tipo] = tipos.get(tipo, 0) + 1
        
        print(f"✅ Base vectorial creada con {len(chunks)} vectores")
        print(f"   📈 Distribución: {', '.join([f'{k}: {v}' for k, v in tipos.items()])}")
        print(f"   🎯 Usando similitud de coseno (más precisa)")
        
    def calcular_relevancia_keywords(self, pregunta, chunk_texto):
        """
        Calcula relevancia adicional basada en keywords
        """
        pregunta_lower = pregunta.lower()
        chunk_lower = chunk_texto.lower()
        
        # Extraer palabras clave de la pregunta (sin palabras vacías)
        palabras_vacias = ['qué', 'cuál', 'cómo', 'dónde', 'cuándo', 'por', 'es', 'son', 
                          'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en']
        
        keywords = [p for p in pregunta_lower.split() 
                   if p not in palabras_vacias and len(p) > 3]
        
        # Contar cuántas keywords aparecen en el chunk
        matches = sum(1 for kw in keywords if kw in chunk_lower)
        
        return matches / len(keywords) if keywords else 0
        
    def buscar_relevantes(self, pregunta, top_k=5):
        """
        Busca los chunks más similares a la pregunta
        MEJORA: Usa expansión de consulta y reranking
        """
        print(f"🔎 Agente Buscador: Buscando información para '{pregunta[:50]}...'")
        
        if self.index is None or len(self.chunks) == 0:
            print("⚠️  Base vectorial no inicializada")
            return []
        
        # MEJORA 1: Expandir consulta
        consulta_expandida = self.expandir_consulta(pregunta)
        
        # Convertir pregunta a embedding
        pregunta_embedding = self.modelo.encode([consulta_expandida])
        pregunta_embedding = pregunta_embedding.astype('float32')
        
        # Normalizar para similitud de coseno
        faiss.normalize_L2(pregunta_embedding)
        
        # MEJORA 2: Buscar más resultados de los necesarios para reranking
        k_busqueda = min(top_k * 3, len(self.chunks))
        similitudes, indices = self.index.search(pregunta_embedding, k_busqueda)
        
        # MEJORA 3: Reranking con keywords
        resultados_con_score = []
        
        for i, idx in enumerate(indices[0]):
            chunk = self.chunks[idx].copy()
            
            # Score semántico (similitud de coseno, ya normalizado entre 0 y 1)
            score_semantico = float(similitudes[0][i])
            
            # Score de keywords
            score_keywords = self.calcular_relevancia_keywords(pregunta, chunk['texto'])
            
            # Score combinado (70% semántico, 30% keywords)
            score_final = (score_semantico * 0.7) + (score_keywords * 0.3)
            
            chunk['score_semantico'] = score_semantico
            chunk['score_keywords'] = score_keywords
            chunk['relevancia'] = score_final
            
            resultados_con_score.append(chunk)
        
        # MEJORA 4: Ordenar por score combinado
        resultados_con_score.sort(key=lambda x: x['relevancia'], reverse=True)
        
        # MEJORA 5: Filtrar por umbral y tomar top_k
        # Umbral: 0.5 = 50% de relevancia mínima
        umbral = 0.5
        resultados_filtrados = [r for r in resultados_con_score if r['relevancia'] >= umbral]
        
        # Si no hay resultados sobre el umbral, tomar los mejores disponibles
        if not resultados_filtrados:
            resultados_filtrados = resultados_con_score[:top_k]
            print(f"   ⚠️  No se encontraron resultados con alta confianza (umbral: {umbral})")
        
        # Tomar solo top_k
        resultados_finales = resultados_filtrados[:top_k]
        
        print(f"✅ {len(resultados_finales)} chunks relevantes encontrados")
        for i, r in enumerate(resultados_finales, 1):
            print(f"   {i}. {r['fuente']} - Score: {r['relevancia']:.3f} "
                  f"(Sem: {r['score_semantico']:.3f}, KW: {r['score_keywords']:.3f})")
        
        return resultados_finales
    
    def buscar_contexto_extendido(self, pregunta, top_k=3):
        """
        Busca chunks relevantes Y sus vecinos para mayor contexto
        """
        resultados_base = self.buscar_relevantes(pregunta, top_k)
        
        # Agregar chunks vecinos para contexto
        resultados_extendidos = []
        indices_usados = set()
        
        for resultado in resultados_base:
            chunk_id = resultado['id']
            
            # Buscar chunks del mismo documento
            partes = chunk_id.rsplit('_', 1)
            if len(partes) == 2:
                nombre_doc, num_str = partes
                num_chunk = int(num_str)
                
                # Agregar chunk anterior y siguiente si existen
                for offset in [-1, 0, 1]:
                    nuevo_id = f"{nombre_doc}_{num_chunk + offset}"
                    if nuevo_id not in indices_usados:
                        chunk_vecino = next((c for c in self.chunks if c['id'] == nuevo_id), None)
                        if chunk_vecino:
                            chunk_copia = chunk_vecino.copy()
                            if offset == 0:
                                chunk_copia['relevancia'] = resultado['relevancia']
                            else:
                                chunk_copia['relevancia'] = resultado['relevancia'] * 0.5
                            resultados_extendidos.append(chunk_copia)
                            indices_usados.add(nuevo_id)
        
        # Ordenar por relevancia
        resultados_extendidos.sort(key=lambda x: x['relevancia'], reverse=True)
        
        return resultados_extendidos[:top_k * 2]  # Devolver más contexto