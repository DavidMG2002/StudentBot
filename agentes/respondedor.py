"""
Agente 3: Respondedor
Responsabilidad: Generar respuesta final basada en los chunks encontrados
MEJORAS DE PRECISIÓN:
- Respuestas más contextualizadas
- Resumen inteligente
- Citas precisas
- Detección de nivel de confianza
"""
import re

class AgenteRespondedor:
    
    def extraer_oraciones_relevantes(self, texto, pregunta, max_oraciones=3):
        """
        Extrae las oraciones más relevantes del texto respecto a la pregunta
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
    
    def calcular_confianza(self, chunks_relevantes):
        """
        Calcula el nivel de confianza de la respuesta basado en los scores
        """
        if not chunks_relevantes:
            return 0.0, "Muy Baja"
        
        # Promedio de relevancia
        scores = [c.get('relevancia', 0) for c in chunks_relevantes]
        promedio = sum(scores) / len(scores)
        
        # Categorizar confianza
        if promedio >= 0.8:
            return promedio, "Muy Alta"
        elif promedio >= 0.6:
            return promedio, "Alta"
        elif promedio >= 0.4:
            return promedio, "Media"
        else:
            return promedio, "Baja"
    
    def generar_respuesta_precisa(self, pregunta, chunks_relevantes):
        """
        Genera una respuesta PRECISA y CONTEXTUALIZADA
        MEJORA: Extrae solo la información más relevante
        """
        print("💬 Agente Respondedor: Generando respuesta precisa...")
        
        if not chunks_relevantes:
            return self._respuesta_no_encontrada()
        
        # Calcular confianza
        confianza_score, confianza_nivel = self.calcular_confianza(chunks_relevantes)
        
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
        icono_confianza = self._obtener_icono_confianza(confianza_nivel)
        respuesta_partes.append(f"{icono_confianza} **Confianza: {confianza_nivel}** ({confianza_score:.2f})\n")
        respuesta_partes.append("---\n\n")
        
        # Información encontrada
        respuesta_partes.append("📚 **Información Relevante:**\n\n")
        
        for fuente, chunks in por_fuente.items():
            respuesta_partes.append(f"**📄 {fuente}**\n\n")
            
            for i, chunk in enumerate(chunks, 1):
                # Extraer oraciones más relevantes
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
        
        # Resumen final
        respuesta_partes.append("---\n\n")
        respuesta_partes.append(self._generar_resumen(pregunta, chunks_relevantes, por_fuente))
        
        respuesta = "".join(respuesta_partes)
        
        print(f"✅ Respuesta generada (Confianza: {confianza_nivel})")
        return respuesta
    
    def generar_respuesta(self, pregunta, chunks_relevantes):
        """Alias para compatibilidad con código existente"""
        return self.generar_respuesta_precisa(pregunta, chunks_relevantes)
    
    def _obtener_icono_confianza(self, nivel):
        """Retorna emoji según nivel de confianza"""
        iconos = {
            "Muy Alta": "🎯",
            "Alta": "✅",
            "Media": "⚠️",
            "Baja": "❓",
            "Muy Baja": "❌"
        }
        return iconos.get(nivel, "❓")
    
    def _crear_barra_relevancia(self, relevancia):
        """Crea una barra visual de relevancia"""
        num_bloques = int(relevancia * 10)
        barra_llena = "█" * num_bloques
        barra_vacia = "░" * (10 - num_bloques)
        return f"[{barra_llena}{barra_vacia}]"
    
    def _generar_resumen(self, pregunta, chunks, por_fuente):
        """Genera un resumen inteligente"""
        total_chunks = len(chunks)
        total_fuentes = len(por_fuente)
        
        # Calcular estadísticas
        tipos_docs = {}
        for chunk in chunks:
            tipo = chunk.get('tipo', 'TXT')
            tipos_docs[tipo] = tipos_docs.get(tipo, 0) + 1
        
        resumen_partes = []
        resumen_partes.append("💡 **Resumen:**\n\n")
        resumen_partes.append(f"• Se encontraron **{total_chunks} fragmentos relevantes** ")
        resumen_partes.append(f"en **{total_fuentes} documento(s)**\n")
        
        # Tipos de documentos
        if tipos_docs:
            tipos_str = ", ".join([f"{v} {k}" for k, v in tipos_docs.items()])
            resumen_partes.append(f"• Tipos: {tipos_str}\n")
        
        # Listar fuentes
        resumen_partes.append("\n📋 **Fuentes consultadas:**\n")
        for fuente in por_fuente.keys():
            num_chunks = len(por_fuente[fuente])
            resumen_partes.append(f"• {fuente} ({num_chunks} fragmento{'s' if num_chunks > 1 else ''})\n")
        
        return "".join(resumen_partes)
    
    def _respuesta_no_encontrada(self):
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
    
    def generar_respuesta_simple(self, pregunta, chunks_relevantes):
        """Versión compacta de la respuesta (para UI minimalistas)"""
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
    
    def generar_respuesta_detallada(self, pregunta, chunks_relevantes):
        """Versión con todos los detalles (para análisis profundo)"""
        if not chunks_relevantes:
            return self._respuesta_no_encontrada()
        
        respuesta_partes = []
        respuesta_partes.append("# 📊 Análisis Detallado\n\n")
        respuesta_partes.append(f"**Pregunta:** {pregunta}\n\n")
        
        # Confianza
        confianza_score, confianza_nivel = self.calcular_confianza(chunks_relevantes)
        respuesta_partes.append(f"**Confianza Global:** {confianza_nivel} ({confianza_score:.2%})\n\n")
        respuesta_partes.append("---\n\n")
        
        # Cada chunk en detalle
        for i, chunk in enumerate(chunks_relevantes, 1):
            respuesta_partes.append(f"## Resultado {i}: {chunk['fuente']}\n\n")
            respuesta_partes.append(f"**Relevancia Total:** {chunk.get('relevancia', 0):.2%}\n")
            respuesta_partes.append(f"- Score Semántico: {chunk.get('score_semantico', 0):.2%}\n")
            respuesta_partes.append(f"- Score Keywords: {chunk.get('score_keywords', 0):.2%}\n\n")
            respuesta_partes.append(f"**Texto:**\n{chunk['texto'][:500]}...\n\n")
            respuesta_partes.append("---\n\n")
        
        return "".join(respuesta_partes)