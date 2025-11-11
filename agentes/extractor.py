"""
Agente 1: Extractor
Responsabilidad: Leer documentos (TXT y PDF) y dividirlos en chunks INTELIGENTES
MEJORAS DE PRECISIÓN:
- Chunks por párrafos (no por caracteres arbitrarios)
- Preserva contexto completo
- Evita cortar frases a la mitad
"""
import os
import PyPDF2
import re

class AgenteExtractor:
    def __init__(self, carpeta_documentos="documentos"):
        self.carpeta = carpeta_documentos
        self.documentos = []
        
    def leer_pdf(self, ruta_archivo):
        """Lee un archivo PDF y extrae todo su texto"""
        try:
            texto_completo = ""
            with open(ruta_archivo, 'rb') as archivo:
                lector_pdf = PyPDF2.PdfReader(archivo)
                num_paginas = len(lector_pdf.pages)
                
                print(f"   📄 Leyendo PDF: {num_paginas} páginas")
                
                for num_pagina in range(num_paginas):
                    pagina = lector_pdf.pages[num_pagina]
                    texto = pagina.extract_text()
                    if texto:
                        # Mantener referencia de página para mejor contexto
                        texto_completo += f"\n[Página {num_pagina + 1}]\n{texto}"
                
            return texto_completo
        except Exception as e:
            print(f"   ⚠️  Error al leer PDF: {str(e)}")
            return ""
    
    def leer_documentos(self):
        """Lee todos los archivos .txt y .pdf de la carpeta"""
        print("🔍 Agente Extractor: Leyendo documentos...")
        
        if not os.path.exists(self.carpeta):
            os.makedirs(self.carpeta)
            print(f"⚠️  Carpeta '{self.carpeta}' creada. Agrega archivos .txt o .pdf ahí.")
            return []
        
        archivos_txt = [f for f in os.listdir(self.carpeta) if f.endswith('.txt')]
        archivos_pdf = [f for f in os.listdir(self.carpeta) if f.endswith('.pdf')]
        
        print(f"   📁 Encontrados: {len(archivos_txt)} TXT, {len(archivos_pdf)} PDF")
        
        # Procesar archivos TXT
        for archivo in archivos_txt[:20]:
            ruta = os.path.join(self.carpeta, archivo)
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.documentos.append({
                        'nombre': archivo,
                        'contenido': contenido,
                        'tipo': 'TXT'
                    })
                    print(f"   ✅ TXT: {archivo}")
            except Exception as e:
                print(f"   ❌ Error leyendo {archivo}: {str(e)}")
        
        # Procesar archivos PDF
        for archivo in archivos_pdf[:20]:
            ruta = os.path.join(self.carpeta, archivo)
            contenido = self.leer_pdf(ruta)
            if contenido.strip():
                self.documentos.append({
                    'nombre': archivo,
                    'contenido': contenido,
                    'tipo': 'PDF'
                })
                print(f"   ✅ PDF: {archivo}")
            else:
                print(f"   ⚠️  PDF vacío o ilegible: {archivo}")
        
        print(f"✅ {len(self.documentos)} documentos leídos en total")
        return self.documentos
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza el texto para mejor procesamiento"""
        # Eliminar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        # Eliminar líneas vacías excesivas
        texto = re.sub(r'\n\s*\n', '\n\n', texto)
        return texto.strip()
    
    def dividir_por_oraciones(self, texto):
        """Divide texto en oraciones completas"""
        # Patrones para detectar fin de oración
        patrones = r'[.!?]+[\s\n]+'
        oraciones = re.split(patrones, texto)
        return [o.strip() for o in oraciones if len(o.strip()) > 20]
    
    def dividir_por_parrafos(self, texto):
        """Divide texto en párrafos (mejor que chunks arbitrarios)"""
        # Dividir por saltos de línea dobles o más
        parrafos = re.split(r'\n\n+', texto)
        return [p.strip() for p in parrafos if len(p.strip()) > 50]
    
    def crear_chunks_inteligentes(self, texto, tamano_objetivo=400):
        """
        Crea chunks inteligentes que respetan límites de párrafos y oraciones
        MEJOR PRECISIÓN: No corta frases a la mitad
        """
        chunks = []
        parrafos = self.dividir_por_parrafos(texto)
        
        chunk_actual = ""
        
        for parrafo in parrafos:
            # Si el párrafo es muy largo, dividir por oraciones
            if len(parrafo) > tamano_objetivo * 1.5:
                oraciones = self.dividir_por_oraciones(parrafo)
                
                for oracion in oraciones:
                    if len(chunk_actual) + len(oracion) < tamano_objetivo:
                        chunk_actual += " " + oracion
                    else:
                        if chunk_actual.strip():
                            chunks.append(chunk_actual.strip())
                        chunk_actual = oracion
            else:
                # Si agregar el párrafo excede el tamaño, guardar chunk actual
                if len(chunk_actual) + len(parrafo) > tamano_objetivo:
                    if chunk_actual.strip():
                        chunks.append(chunk_actual.strip())
                    chunk_actual = parrafo
                else:
                    chunk_actual += "\n\n" + parrafo
        
        # Agregar último chunk
        if chunk_actual.strip():
            chunks.append(chunk_actual.strip())
        
        return chunks
    
    def crear_chunks(self, tamano_chunk=400):
        """
        Divide el texto en chunks INTELIGENTES
        MEJORA: Usa párrafos y oraciones completas en lugar de caracteres arbitrarios
        """
        print(f"✂️  Agente Extractor: Creando chunks inteligentes (objetivo: {tamano_chunk} caracteres)...")
        
        chunks = []
        for doc in self.documentos:
            texto = doc['contenido']
            nombre = doc['nombre']
            tipo = doc.get('tipo', 'TXT')
            
            # Limpiar texto
            texto_limpio = self.limpiar_texto(texto)
            
            # Crear chunks inteligentes
            chunks_doc = self.crear_chunks_inteligentes(texto_limpio, tamano_chunk)
            
            # Agregar metadatos a cada chunk
            for i, chunk_texto in enumerate(chunks_doc):
                chunks.append({
                    'texto': chunk_texto,
                    'fuente': f"{nombre} ({tipo})",
                    'id': f"{nombre}_{i}",
                    'tipo': tipo,
                    'numero_chunk': i + 1,
                    'total_chunks': len(chunks_doc)
                })
        
        print(f"✅ {len(chunks)} chunks inteligentes creados")
        
        # Mostrar estadísticas
        tamanos = [len(c['texto']) for c in chunks]
        promedio = sum(tamanos) / len(tamanos) if tamanos else 0
        print(f"   📊 Tamaño promedio: {promedio:.0f} caracteres")
        print(f"   📏 Rango: {min(tamanos) if tamanos else 0} - {max(tamanos) if tamanos else 0} caracteres")
        
        return chunks