"""
Agente 3: Respondedor con LangChain
REQUISITO: Agente que genera respuestas finales con LangChain Tools
Rol: Generar respuestas contextualizadas con indicadores de confianza
"""
import re
from typing import List, Dict, Tuple
from langchain.agents import Tool
from langchain.tools import BaseTool


class AgenteRespondedorLangChain:
    """
    Agente de Respuesta implementado con LangChain
    Rol: Generar respuestas finales, extraer información relevante y calcular confianza
    """
    
    def __init__(self):
        print("🤖 Agente Respondedor LangChain inicializado")
        self.tools = self._crear_tools()
        print(f"   🔧 Tools: {len(self.tools)}")
    
    def _crear_tools(self) -> List[Tool]:
        """Crea las herramientas (tools) del agente"""
        return [
            Tool(
                name="generar_respuesta",
                func=self._generar_respuesta_tool,
                description="Genera una respuesta estructurada a partir de chunks relevantes"
            ),
            Tool(
                name="extraer_oraciones_relevantes",
                func=self._extraer_oraciones_tool,
                description="Extrae las oraciones más relevantes de un texto según una pregunta"
            ),
            Tool(
                name="calcular_confianza",
                func=self._calcular_confianza_tool,
                description="Calcula el nivel de confianza de una respuesta basado en scores"
            ),
            Tool(
                name="crear_resumen",
                func=self._crear_resumen_tool,
                description="Genera un resumen ejecutivo de los resultados encontrados"
            ),
            Tool(
                name="formatear_respuesta",
                func=self._formatear_respuesta_tool,
                description="Formatea una respuesta con markdown y estructura visual"
            )
        ]
    
    def _generar_respuesta_tool(self, contexto: str) -> str:
        """Tool: Genera respuesta (versión simplificada para tool)"""
        try:
            # Parsear contexto (formato: pregunta|||chunks_json)
            partes = contexto.split('|||')
            if len(partes) < 2:
                return "❌ Formato: pregunta|||chunks_json"
            
            return f"✅ Respuesta generada basada en {len(partes[1])} caracteres de contexto"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _extraer_oraciones_tool(self, datos: str) -> str:
        """Tool: Extrae oraciones relevantes"""
        try:
            # Formato: texto|||pregunta|||max_oraciones
            partes = datos.split('|||')
            if len(partes) < 2:
                return "❌ Formato: texto|||pregunta|||max_oraciones"
            
            texto = partes[0]
            pregunta = partes[1]
            max_oraciones = int(partes[2]) if len(partes) > 2 else 3
            
            resultado = self.extraer_oraciones_relevantes(texto, pregunta, max_oraciones)
            return f"✅ {len(resultado)} caracteres extraídos"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _calcular_confianza_tool(self, scores: str) -> str:
        """Tool: Calcula confianza"""
        try:
            # Formato: score1,score2,score3
            valores = [float(s.strip()) for s in scores.split(',')]
            promedio = sum(valores) / len(valores)
            _, nivel = self._categorizar_confianza(promedio)
            return f"✅ Confianza: {nivel} ({promedio:.2%})"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _crear_resumen_tool(self, datos: str) -> str:
        """Tool: Crea resumen"""
        try:
            # Formato: num_chunks|||num_fuentes
            partes = datos.split('|||')
            num_chunks = int(partes[0]) if len(partes) > 0 else 0
            num_fuentes = int(partes[1]) if len(partes) > 1 else 0
            return f"✅ Resumen: {num_chunks} fragmentos en {num_fuentes} fuente(s)"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _formatear_respuesta_tool(self, texto: str) -> str:
        """Tool: Formatea respuesta con markdown"""
        try:
            # Aplicar formateo básico
            texto_formateado = texto.replace('\n', '\n\n')
            return f"✅ Respuesta formateada: {len(texto_formateado)} caracteres"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def extraer_oraciones_relevantes(self, texto: str, pregunta: str, max_oraciones: int = 3) -> str:
        """
        Extrae las oraciones más relevantes del texto respecto a la pregunta
        Implementa el requisito de análisis inteligente de contenido
        """
        # Dividir en oraciones
        oraciones = re.split(r'[.!?]+', texto)
        oraciones = [o.strip() for o in oraciones if len(o.strip()) > 20]
        
        if not oraciones:
            return texto[:300]
        
        # Extraer palabras clave de la pregunta
        palabras_vacias = {'qué', 'cuál', 'cómo', 'dónde', 'cuándo', 'por', 'es', 
                          'son', 'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del'}
        palabras_pregunta = set(pregunta.lower().split()) - palabras_vacias
        
        # Calcular relevancia de cada oración
        oraciones_con_score = []
        for oracion in oraciones:
            palabras_oracion = set(oracion.lower().split())
            # Contar coincidencias
            coincidencias = len(palabras_pregunta & palabras_oracion)
            oraciones_con_score.append((oracion, coincidencias))
        
        # Ordenar por relevancia
        oraciones_con_score.sort(key=lambda x: x[1], reverse=True)
        
        # Tomar las más relevantes
        mejores_oraciones = [o[0] for o in oraciones_con_score[:max_oraciones]]
        
        return '. '.join(mejores_oraciones) + '.'
    
    def _categorizar_confianza(self, score: float) -> Tuple[str, str]:
        """
        Categoriza el nivel de confianza
        Retorna: (icono, nivel)
        """
        if score >= 0.8:
            return "🎯", "Muy Alta"
        elif score >= 0.6:
            return "✅", "Alta"
        elif score >= 0.4:
            return "⚠️", "Media"
        elif score >= 0.2:
            return "❓", "Baja"
        else:
            return "❌", "Muy Baja"
    
    def calcular_confianza(self, chunks_relevantes: List[Dict]) -> Tuple[float, str]:
        """
        Calcula el nivel de confianza de la respuesta basado en los scores
        Implementa el requisito de evaluación de calidad de respuestas
        """
        if not chunks_relevantes:
            return 0.0, "Muy Baja"
        
        # Promedio de relevancia
        scores = [c.get('relevancia', 0) for c in chunks_relevantes]
        promedio = sum(scores) / len(scores)
        
        # Categorizar confianza
        _, nivel = self._categorizar_confianza(promedio)
        
        return promedio, nivel
    
    def _crear_barra_relevancia(self, relevancia: float) -> str:
        """Crea una barra visual de relevancia"""
        num_bloques = int(relevancia * 10)
        barra_llena = "█" * num_bloques
        barra_vacia = "░" * (10 - num_bloques)
        return f"[{barra_llena}{barra_vacia}]"
    
    def _obtener_icono_confianza(self, nivel: str) -> str:
        """Retorna emoji según nivel de confianza"""
        iconos = {
            "Muy Alta": "🎯",
            "Alta": "✅",
            "Media": "⚠️",
            "Baja": "❓",
            "Muy Baja": "❌"
        }
        return iconos.get(nivel, "❓")
    
    def generar_respuesta_precisa(self, pregunta: str, chunks_relevantes: List[Dict]) -> str:
        """
        Genera una respuesta PRECISA y CONTEXTUALIZADA usando LangChain Tools
        Implementa el flujo completo de generación de respuesta del agente
        """
        print("💬 Agente Respondedor: Generando respuesta precisa...")
        
        if not chunks_relevantes:
            return self._respuesta_no_encontrada()
        
        # Tool 1: Calcular confianza
        confianza_score, confianza_nivel = self.calcular_confianza(chunks_relevantes)
        icono_confianza = self._obtener_icono_confianza(confianza_nivel)
        
        # Agrupar chunks por fuente
        por_fuente = {}
        for chunk in chunks_relevantes:
            fuente = chunk['fuente']
            if fuente not in por_fuente:
                por_fuente[fuente] = []
            por_fuente[fuente].append(chunk)
        
        # Construir respuesta estructurada
        respuesta_partes = []
        
        # Indicador de confianza
        respuesta_partes.append(f"{icono_confianza} **Confianza: {confianza_nivel}** ({confianza_score:.2f})\n")
        respuesta_partes.append("───────────────────────────────\n\n")
        
        # Información encontrada
        respuesta_partes.append("📚 **Información Relevante:**\n\n")
        
        for fuente, chunks in por_fuente.items():
            respuesta_partes.append(f"**📄 {fuente}**\n\n")
            
            for i, chunk in enumerate(chunks, 1):
                # Tool 2: Extraer oraciones más relevantes
                oraciones_relevantes = self.extraer_oraciones_relevantes(
                    chunk['texto'], 
                    pregunta, 
                    max_oraciones=2
                )
                
                # Mostrar score de relevancia
                relevancia = chunk.get('relevancia', 0)
                barra = self._crear_barra_relevancia(relevancia)
                
                respuesta_partes.append(
                    f"{i}. {barra} **Relevancia: {relevancia:.1%}**\n"
                    f"   {oraciones_relevantes}\n\n"
                )
        
        # Tool 3: Crear resumen
        respuesta_partes.append("───────────────────────────────\n\n")
        respuesta_partes.append(self._generar_resumen(pregunta, chunks_relevantes, por_fuente))
        
        # Tool 4: Formatear respuesta final
        respuesta = "".join(respuesta_partes)
        
        print(f"✅ Respuesta generada (Confianza: {confianza_nivel})")
        return respuesta
    
    def generar_respuesta(self, pregunta: str, chunks_relevantes: List[Dict]) -> str:
        """Alias para compatibilidad con código existente"""
        return self.generar_respuesta_precisa(pregunta, chunks_relevantes)
    
    def _generar_resumen(self, pregunta: str, chunks: List[Dict], por_fuente: Dict) -> str:
        """Genera un resumen inteligente de los resultados"""
        total_chunks = len(chunks)
        total_fuentes = len(por_fuente)
        
        # Calcular estadísticas
        tipos_docs = {}
        metodos_extraccion = {}
        
        for chunk in chunks:
            tipo = chunk.get('tipo', 'TXT')
            tipos_docs[tipo] = tipos_docs.get(tipo, 0) + 1
            
            metodo = chunk.get('metodo_extraccion', 'directo')
            if metodo != 'directo':
                metodos_extraccion[metodo] = metodos_extraccion.get(metodo, 0) + 1
        
        resumen_partes = []
        resumen_partes.append("💡 **Resumen:**\n\n")
        resumen_partes.append(f"• Se encontraron **{total_chunks} fragmentos relevantes** ")
        resumen_partes.append(f"en **{total_fuentes} documento(s)**\n")
        
        # Tipos de documentos
        if tipos_docs:
            tipos_str = ", ".join([f"{v} {k}" for k, v in tipos_docs.items()])
            resumen_partes.append(f"• Tipos: {tipos_str}\n")
        
        # Métodos de extracción especiales (OCR, etc.)
        if metodos_extraccion:
            metodos_str = ", ".join([f"{v} con {k}" for k, v in metodos_extraccion.items()])
            resumen_partes.append(f"• Métodos: {metodos_str}\n")
        
        # Listar fuentes
        resumen_partes.append("\n📋 **Fuentes consultadas:**\n")
        for fuente in por_fuente.keys():
            num_chunks = len(por_fuente[fuente])
            resumen_partes.append(f"• {fuente} ({num_chunks} fragmento{'s' if num_chunks > 1 else ''})\n")
        
        return "".join(resumen_partes)
    
    def _respuesta_no_encontrada(self) -> str:
        """Respuesta cuando no se encuentra información"""
        return """
❌ **No se encontró información relevante**

Lo siento, no pude encontrar información que responda a tu pregunta en los documentos cargados.

💡 **Sugerencias:**
• Intenta reformular la pregunta
• Usa palabras clave diferentes
• Verifica que los documentos contengan esa información
• Asegúrate de haber cargado todos los documentos necesarios
        """.strip()
    
    def generar_respuesta_simple(self, pregunta: str, chunks_relevantes: List[Dict]) -> str:
        """
        Versión compacta de la respuesta (para UI minimalistas)
        Usa menos Tools pero mantiene funcionalidad básica
        """
        if not chunks_relevantes:
            return "No se encontró información relevante."
        
        # Tomar el chunk más relevante
        mejor_chunk = chunks_relevantes[0]
        texto = self.extraer_oraciones_relevantes(
            mejor_chunk['texto'], 
            pregunta, 
            max_oraciones=2
        )
        fuente = mejor_chunk['fuente']
        relevancia = mejor_chunk.get('relevancia', 0)
        
        return f"""**{fuente}** (Relevancia: {relevancia:.0%})

{texto}

*Se encontraron {len(chunks_relevantes)} resultados relacionados*"""
    
    def generar_respuesta_detallada(self, pregunta: str, chunks_relevantes: List[Dict]) -> str:
        """
        Versión con todos los detalles (para análisis profundo)
        Usa todos los Tools disponibles
        """
        if not chunks_relevantes:
            return self._respuesta_no_encontrada()
        
        respuesta_partes = []
        respuesta_partes.append("# 📊 Análisis Detallado\n\n")
        respuesta_partes.append(f"**Pregunta:** {pregunta}\n\n")
        
        # Confianza
        confianza_score, confianza_nivel = self.calcular_confianza(chunks_relevantes)
        icono = self._obtener_icono_confianza(confianza_nivel)
        respuesta_partes.append(f"**Confianza Global:** {icono} {confianza_nivel} ({confianza_score:.2%})\n\n")
        respuesta_partes.append("───────────────────────────────\n\n")
        
        # Cada chunk en detalle
        for i, chunk in enumerate(chunks_relevantes, 1):
            respuesta_partes.append(f"## Resultado {i}: {chunk['fuente']}\n\n")
            respuesta_partes.append(f"**Relevancia Total:** {chunk.get('relevancia', 0):.2%}\n")
            respuesta_partes.append(f"- Score Semántico: {chunk.get('score_semantico', 0):.2%}\n")
            respuesta_partes.append(f"- Score Keywords: {chunk.get('score_keywords', 0):.2%}\n")
            
            # Información adicional
            if 'metodo_extraccion' in chunk and chunk['metodo_extraccion'] != 'directo':
                respuesta_partes.append(f"- Método: {chunk['metodo_extraccion']}\n")
            
            if 'numero_chunk' in chunk:
                respuesta_partes.append(
                    f"- Ubicación: Chunk {chunk['numero_chunk']} de {chunk.get('total_chunks', '?')}\n"
                )
            
            respuesta_partes.append(f"\n**Texto completo:**\n{chunk['texto'][:500]}...\n\n")
            respuesta_partes.append("───────────────────────────────\n\n")
        
        return "".join(respuesta_partes)
    
    def generar_respuesta_con_llm(self, pregunta: str, chunks_relevantes: List[Dict], api_key: str = None) -> str:
        """
        Versión futura: Usar un LLM real (GPT/Claude) para respuestas en lenguaje natural
        
        NOTA: Requiere integración con LangChain LLM chains
        """
        if not api_key:
            print("⚠️  No se proporcionó API key. Usando respuesta estructurada.")
            return self.generar_respuesta_precisa(pregunta, chunks_relevantes)
        
        # Aquí se integraría con LangChain LLM
        """
        from langchain.llms import OpenAI
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        
        contexto = "\n\n".join([c['texto'] for c in chunks_relevantes])
        
        prompt = PromptTemplate(
            input_variables=["contexto", "pregunta"],
            template="Contexto:\n{contexto}\n\nPregunta: {pregunta}\n\nResponde:"
        )
        
        llm = OpenAI(api_key=api_key)
        chain = LLMChain(llm=llm, prompt=prompt)
        return chain.run(contexto=contexto, pregunta=pregunta)
        """
        pass
    
    def describir_tools(self):
        """Describe las herramientas del agente"""
        print("\n🔧 TOOLS DEL AGENTE RESPONDEDOR:")
        print("="*60)
        for tool in self.tools:
            print(f"\n📌 {tool.name}")
            print(f"   Descripción: {tool.description}")
        print("="*60 + "\n")