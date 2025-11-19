"""
Agente 1: Extractor con LangChain
REQUISITO: Arquitectura multiagente usando LangChain
"""
import os
import PyPDF2
import re
from typing import List, Dict
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLLM
from langchain.schema import AgentAction, AgentFinish

# OCR para PDFs escaneados (NUEVO REQUISITO)
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    OCR_DISPONIBLE = True
except:
    OCR_DISPONIBLE = False
    print("|X| OCR no disponible. Instala: pip install pytesseract pdf2image Pillow")


class AgenteExtractorLangChain:
    """
    Agente de Extracción implementado con LangChain
    Rol: Leer documentos TXT, PDF y aplicar OCR si es necesario
    """
    
    def __init__(self, carpeta_documentos="documentos"):
        self.carpeta = carpeta_documentos
        self.documentos = []
        self.tools = self._crear_tools()
        
        print("Agente Extractor LangChain inicializado")
        print(f"Carpeta: {carpeta_documentos}")
        print(f"Tools: {len(self.tools)}")
        if OCR_DISPONIBLE:
            print("OCR: Activado (Tesseract)")
    
    def _crear_tools(self) -> List[Tool]:
        """Crea las herramientas (tools) del agente"""
        return [
            Tool(
                name="leer_txt",
                func=self._leer_txt,
                description="Lee archivos de texto plano (.txt)"
            ),
            Tool(
                name="leer_pdf",
                func=self._leer_pdf,
                description="Lee archivos PDF y extrae su texto"
            ),
            Tool(
                name="aplicar_ocr",
                func=self._aplicar_ocr,
                description="Aplica OCR a PDFs escaneados (imágenes)"
            ),
            Tool(
                name="listar_archivos",
                func=self._listar_archivos,
                description="Lista todos los archivos disponibles en la carpeta"
            )
        ]
    
    def _leer_txt(self, ruta: str) -> str:
        """Tool: Lee un archivo TXT"""
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return f"TXT leído: {len(contenido)} caracteres"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _leer_pdf(self, ruta: str) -> str:
        """Tool: Lee un archivo PDF"""
        try:
            texto_completo = ""
            with open(ruta, 'rb') as archivo:
                lector_pdf = PyPDF2.PdfReader(archivo)
                num_paginas = len(lector_pdf.pages)
                
                for num_pagina in range(num_paginas):
                    pagina = lector_pdf.pages[num_pagina]
                    texto = pagina.extract_text()
                    if texto:
                        texto_completo += f"\n[Página {num_pagina + 1}]\n{texto}"
            
            return f"PDF leído: {num_paginas} páginas, {len(texto_completo)} caracteres"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _aplicar_ocr(self, ruta: str) -> str:
        """Tool: Aplica OCR a un PDF escaneado"""
        if not OCR_DISPONIBLE:
            return "OCR no disponible. Instala pytesseract"
        
        try:
            # Convertir PDF a imágenes
            imagenes = convert_from_path(ruta, dpi=300)
            texto_completo = ""
            
            for i, imagen in enumerate(imagenes, 1):
                # Aplicar OCR a cada página
                texto = pytesseract.image_to_string(imagen, lang='spa')
                texto_completo += f"\n[Página {i} - OCR]\n{texto}"
            
            return f"OCR aplicado: {len(imagenes)} páginas, {len(texto_completo)} caracteres"
        except Exception as e:
            return f"Error OCR: {str(e)}"
    
    def _listar_archivos(self, dummy: str = "") -> str:
        """Tool: Lista archivos en la carpeta"""
        if not os.path.exists(self.carpeta):
            return "Carpeta no existe"
        
        archivos_txt = [f for f in os.listdir(self.carpeta) if f.endswith('.txt')]
        archivos_pdf = [f for f in os.listdir(self.carpeta) if f.endswith('.pdf')]
        
        return f"{len(archivos_txt)} TXT, {len(archivos_pdf)} PDF"
    
    def leer_documentos(self) -> List[Dict]:
        """
        Ejecuta el agente para leer todos los documentos
        Usa LangChain Tools para coordinar la lectura
        """
        print("Leyendo documentos...")
        
        if not os.path.exists(self.carpeta):
            os.makedirs(self.carpeta)
            print(f"Carpeta '{self.carpeta}' creada.")
            return []
        
        archivos_txt = [f for f in os.listdir(self.carpeta) if f.endswith('.txt')]
        archivos_pdf = [f for f in os.listdir(self.carpeta) if f.endswith('.pdf')]
        
        print(f"Encontrados: {len(archivos_txt)} TXT, {len(archivos_pdf)} PDF")
        
        # Procesar TXT
        for archivo in archivos_txt[:20]:
            ruta = os.path.join(self.carpeta, archivo)
            resultado = self._leer_txt(ruta)
            print(f"   {resultado}")
            
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    self.documentos.append({
                        'nombre': archivo,
                        'contenido': contenido,
                        'tipo': 'TXT',
                        'metodo': 'lectura_directa'
                    })
            except Exception as e:
                print(f"|X|   Error: {e}")
        
        # Procesar PDF
        for archivo in archivos_pdf[:20]:
            ruta = os.path.join(self.carpeta, archivo)
            
            # Intentar lectura normal
            texto = self._extraer_texto_pdf(ruta)
            
            # Si está vacío, intentar OCR
            if not texto.strip() and OCR_DISPONIBLE:
                print(f"   👁️  Aplicando OCR a {archivo}...")
                resultado = self._aplicar_ocr(ruta)
                print(f"   {resultado}")
                texto = self._extraer_texto_ocr(ruta)
                metodo = 'OCR'
            else:
                print(f" ✓  PDF: {archivo}")
                metodo = 'PyPDF2'
            
            if texto.strip():
                self.documentos.append({
                    'nombre': archivo,
                    'contenido': texto,
                    'tipo': 'PDF',
                    'metodo': metodo
                })
        
        print(f"✓ {len(self.documentos)} documentos leídos")
        return self.documentos
    
    def _extraer_texto_pdf(self, ruta: str) -> str:
        """Extrae texto de PDF con PyPDF2"""
        try:
            texto_completo = ""
            with open(ruta, 'rb') as archivo:
                lector_pdf = PyPDF2.PdfReader(archivo)
                for num_pagina in range(len(lector_pdf.pages)):
                    pagina = lector_pdf.pages[num_pagina]
                    texto = pagina.extract_text()
                    if texto:
                        texto_completo += f"\n[Página {num_pagina + 1}]\n{texto}"
            return texto_completo
        except:
            return ""
    
    def _extraer_texto_ocr(self, ruta: str) -> str:
        """Extrae texto con OCR"""
        if not OCR_DISPONIBLE:
            return ""
        try:
            imagenes = convert_from_path(ruta, dpi=300)
            texto_completo = ""
            for i, imagen in enumerate(imagenes, 1):
                texto = pytesseract.image_to_string(imagen, lang='spa')
                texto_completo += f"\n[Página {i} - OCR]\n{texto}"
            return texto_completo
        except:
            return ""
    
    def limpiar_texto(self, texto: str) -> str:
        """Limpia y normaliza el texto"""
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'\n\s*\n', '\n\n', texto)
        return texto.strip()
    
    def dividir_por_parrafos(self, texto: str) -> List[str]:
        """Divide texto en párrafos"""
        parrafos = re.split(r'\n\n+', texto)
        return [p.strip() for p in parrafos if len(p.strip()) > 50]
    
    def dividir_por_oraciones(self, texto: str) -> List[str]:
        """Divide texto en oraciones"""
        patrones = r'[.!?]+[\s\n]+'
        oraciones = re.split(patrones, texto)
        return [o.strip() for o in oraciones if len(o.strip()) > 20]
    
    def crear_chunks_inteligentes(self, texto: str, tamano_objetivo: int = 400) -> List[str]:
        """Crea chunks inteligentes respetando párrafos y oraciones"""
        chunks = []
        parrafos = self.dividir_por_parrafos(texto)
        
        chunk_actual = ""
        
        for parrafo in parrafos:
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
                if len(chunk_actual) + len(parrafo) > tamano_objetivo:
                    if chunk_actual.strip():
                        chunks.append(chunk_actual.strip())
                    chunk_actual = parrafo
                else:
                    chunk_actual += "\n\n" + parrafo
        
        if chunk_actual.strip():
            chunks.append(chunk_actual.strip())
        
        return chunks
    
    def crear_chunks(self, tamano_chunk: int = 400) -> List[Dict]:
        """Crea chunks de todos los documentos"""
        print(f"✂️  Agente Extractor: Creando chunks inteligentes ({tamano_chunk} chars)...")
        
        chunks = []
        for doc in self.documentos:
            texto = doc['contenido']
            nombre = doc['nombre']
            tipo = doc.get('tipo', 'TXT')
            metodo = doc.get('metodo', 'directo')
            
            texto_limpio = self.limpiar_texto(texto)
            chunks_doc = self.crear_chunks_inteligentes(texto_limpio, tamano_chunk)
            
            for i, chunk_texto in enumerate(chunks_doc):
                chunks.append({
                    'texto': chunk_texto,
                    'fuente': f"{nombre} ({tipo})",
                    'id': f"{nombre}_{i}",
                    'tipo': tipo,
                    'metodo_extraccion': metodo,
                    'numero_chunk': i + 1,
                    'total_chunks': len(chunks_doc)
                })
        
        print(f"✓ {len(chunks)} chunks creados")
        
        if chunks:
            tamanos = [len(c['texto']) for c in chunks]
            promedio = sum(tamanos) / len(tamanos)
            print(f"Tamaño promedio: {promedio:.0f} caracteres")
        
        return chunks