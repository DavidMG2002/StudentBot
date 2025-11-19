"""
Agente 4: Mejorador de Respuestas con Gemini Flash 2.0
Responsabilidad: Convertir respuestas técnicas en lenguaje natural
"""
import google.generativeai as genai
from typing import List, Dict
from langchain.agents import Tool

class AgenteMejoradorGemini:
    """
    Agente que usa Gemini Flash 2.0 para mejorar respuestas
    Rol: Transformar fragmentos técnicos en respuestas naturales
    """
    
    def __init__(self, api_key: str = None):
        print("Agente Mejorador Gemini inicializando...")
        
        self.api_key = api_key
        self.modelo = None
        self.habilitado = False
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.modelo = genai.GenerativeModel('gemini-2.0-flash')
                self.habilitado = True
                print("✓ Gemini Flash 2.0 conectado")
                print("Modo: Mejorador de Respuestas")
            except Exception as e:
                print(f"   |X|  Error al conectar Gemini: {e}")
                print("o- Sistema funcionará sin mejoras de Gemini")
        else:
            print("o- Sin API key - Gemini deshabilitado")
        
        self.tools = self._crear_tools()
        print(f"Tools: {len(self.tools)}")
    
    def _crear_tools(self) -> List[Tool]:
        """Crea las herramientas del agente"""
        return [
            Tool(
                name="mejorar_respuesta",
                func=self._mejorar_respuesta_tool,
                description="Mejora una respuesta técnica a lenguaje natural"
            ),
            Tool(
                name="generar_resumen",
                func=self._generar_resumen_tool,
                description="Genera un resumen ejecutivo de chunks"
            ),
            Tool(
                name="responder_conversacional",
                func=self._responder_conversacional_tool,
                description="Responde de forma natural y conversacional"
            )
        ]
    
    def _mejorar_respuesta_tool(self, texto: str) -> str:
        """Tool: Mejora respuesta (wrapper para logging)"""
        if not self.habilitado:
            return "⚠️ Gemini no habilitado"
        return "✓ Respuesta mejorada con Gemini"
    
    def _generar_resumen_tool(self, texto: str) -> str:
        """Tool: Genera resumen"""
        if not self.habilitado:
            return "⚠️ Gemini no habilitado"
        return "✓ Resumen generado"
    
    def _responder_conversacional_tool(self, pregunta: str) -> str:
        """Tool: Respuesta conversacional"""
        if not self.habilitado:
            return "⚠️ Gemini no habilitado"
        return "✓ Respuesta conversacional generada"
    
    def mejorar_respuesta(self, pregunta: str, chunks_relevantes: List[Dict], 
                         respuesta_base: str) -> str:
        """
        Mejora una respuesta usando Gemini Flash 2.0
        
        Args:
            pregunta: Pregunta del usuario
            chunks_relevantes: Chunks encontrados por el buscador
            respuesta_base: Respuesta estructurada del respondedor
            
        Returns:
            Respuesta mejorada en lenguaje natural
        """
        if not self.habilitado:
            print("o- Gemini deshabilitado - devolviendo respuesta base")
            return respuesta_base
        
        print("Agente Gemini: Mejorando respuesta...")
        
        try:
            # Preparar contexto
            contexto = self._preparar_contexto(chunks_relevantes)
            
            # Crear prompt para Gemini
            prompt = self._crear_prompt_mejorador(pregunta, contexto, respuesta_base)
            
            # Generar respuesta mejorada
            response = self.modelo.generate_content(prompt)
            respuesta_mejorada = response.text
            
            print(f"✓ Respuesta mejorada ({len(respuesta_mejorada)} caracteres)")
            
            return respuesta_mejorada
            
        except Exception as e:
            print(f"|X| Error en Gemini: {e}")
            print("o- Devolviendo respuesta base")
            return respuesta_base
    
    def _preparar_contexto(self, chunks: List[Dict]) -> str:
        """Prepara el contexto de los chunks para Gemini"""
        contexto_partes = []
        
        for i, chunk in enumerate(chunks, 1):
            fuente = chunk.get('fuente', 'Desconocido')
            texto = chunk.get('texto', '')
            relevancia = chunk.get('relevancia', 0)
            
            contexto_partes.append(
                f"[Fragmento {i} - {fuente} - Relevancia: {relevancia:.0%}]\n{texto}\n"
            )
        
        return "\n".join(contexto_partes)
    
    def _crear_prompt_mejorador(self, pregunta: str, contexto: str, 
                                respuesta_base: str) -> str:
        """Crea el prompt optimizado para Gemini"""
        
        prompt = f"""Eres un asistente inteligente experto en explicar información de forma clara y natural.

**Tu tarea:** Transformar la respuesta técnica en una respuesta conversacional y fácil de entender.

**PREGUNTA DEL USUARIO:**
{pregunta}

**INFORMACIÓN ENCONTRADA EN LOS DOCUMENTOS:**
{contexto}

**RESPUESTA BASE (formato técnico):**
{respuesta_base}

**INSTRUCCIONES:**
1. Responde la pregunta de forma directa y natural (como si hablaras con un amigo)
2. Usa la información de los fragmentos pero NO copies texto literal
3. Mantén un tono conversacional y amigable
4. Si hay información relevante en varios fragmentos, intégralos en una narrativa coherente
5. Evita usar formato markdown excesivo (solo usa ** para énfasis cuando sea necesario)
6. Al final, menciona brevemente las fuentes consultadas
7. Si la pregunta no se puede responder completamente, sé honesto al respecto

**EJEMPLO DE ESTILO DESEADO:**
"Basándome en los documentos, el emprendimiento es el proceso de identificar y desarrollar oportunidades de negocio. Los emprendedores son personas que detectan necesidades en el mercado y crean soluciones innovadoras.

Hay tres tipos principales que encontré: el emprendimiento de oportunidad (cuando detectas una necesidad del mercado), por necesidad (cuando necesitas generar ingresos), y el social (enfocado en impacto social).

Esta información viene de tu documento de Emprendimiento.pdf."

**AHORA, GENERA TU RESPUESTA MEJORADA:**"""

        return prompt
    
    def generar_resumen_documento(self, documento_nombre: str, chunks: List[Dict]) -> str:
        """
        Genera un resumen ejecutivo de un documento completo
        
        Args:
            documento_nombre: Nombre del documento
            chunks: Todos los chunks del documento
            
        Returns:
            Resumen ejecutivo estructurado
        """
        if not self.habilitado:
            return f"|X| Gemini deshabilitado - No se puede generar resumen de {documento_nombre}"
        
        print(f"Agente Gemini: Generando resumen de {documento_nombre}...")
        
        try:
            # Preparar contenido
            contenido = "\n\n".join([c.get('texto', '') for c in chunks])
            
            # Crear prompt
            prompt = f"""Genera un resumen ejecutivo profesional del siguiente documento:

**DOCUMENTO:** {documento_nombre}

**CONTENIDO:**
{contenido[:15000]}  

**GENERA UN RESUMEN CON ESTA ESTRUCTURA:**

 RESUMEN: {documento_nombre}

 Idea Principal:
[1-2 oraciones sobre el tema central]

 Puntos Clave:
• [Punto importante 1]
• [Punto importante 2]
• [Punto importante 3]
• [etc.]

 Conceptos Importantes:
- [Concepto 1 y breve explicación]
- [Concepto 2 y breve explicación]

 Conclusión:
[Síntesis final en 1-2 oraciones]

**Genera el resumen ahora:**"""

            response = self.modelo.generate_content(prompt)
            resumen = response.text
            
            print(f"✓ Resumen generado ({len(resumen)} caracteres)")
            
            return resumen
            
        except Exception as e:
            print(f"|X| Error al generar resumen: {e}")
            return f"|X| No se pudo generar resumen de {documento_nombre}"
    
    def responder_con_contexto(self, pregunta: str, chunks: List[Dict], 
                              historial: List[Dict] = None) -> str:
        """
        Responde considerando el historial de conversación
        
        Args:
            pregunta: Pregunta actual
            chunks: Chunks relevantes
            historial: Conversaciones previas
            
        Returns:
            Respuesta contextualizada
        """
        if not self.habilitado:
            return "|X| Gemini deshabilitado para modo conversacional"
        
        print("Agente Gemini: Respuesta conversacional...")
        
        try:
            contexto_docs = self._preparar_contexto(chunks)
            contexto_historial = self._preparar_historial(historial)
            
            prompt = f"""Eres un asistente conversacional inteligente.

**HISTORIAL DE LA CONVERSACIÓN:**
{contexto_historial}

**INFORMACIÓN EN LOS DOCUMENTOS:**
{contexto_docs}

**PREGUNTA ACTUAL:**
{pregunta}

**INSTRUCCIONES:**
1. Considera el contexto de la conversación anterior
2. Si la pregunta hace referencia a algo previo ("eso", "el primero", etc.), usa el historial
3. Responde de forma natural y directa
4. Mantén coherencia con lo que dijiste antes

**TU RESPUESTA:**"""

            response = self.modelo.generate_content(prompt)
            respuesta = response.text
            
            print(f"✓ Respuesta conversacional generada")
            
            return respuesta
            
        except Exception as e:
            print(f"|X| Error: {e}")
            return "Lo siento, hubo un error al procesar tu pregunta."
    
    def _preparar_historial(self, historial: List[Dict]) -> str:
        """Prepara el historial de conversación"""
        if not historial:
            return "[No hay historial previo]"
        
        historial_texto = []
        for item in historial[-5:]:  # Últimos 5 intercambios
            rol = item.get('rol', 'usuario')
            if rol == 'usuario':
                pregunta = item.get('pregunta', '')
                historial_texto.append(f"Usuario: {pregunta}")
            else:
                respuesta = item.get('respuesta', '')[:200]
                historial_texto.append(f"Asistente: {respuesta}...")
        
        return "\n".join(historial_texto)
    
    def verificar_estado(self) -> Dict:
        """Verifica el estado del agente Gemini"""
        return {
            'habilitado': self.habilitado,
            'modelo': 'gemini-2.0-flash-exp' if self.habilitado else None,
            'api_key_presente': bool(self.api_key),
            'tools': len(self.tools)
        }