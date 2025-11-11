"""
Backend API con Flask - VERSIÓN MEJORADA CON MAYOR PRECISIÓN
Endpoints para el frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import time

sys.path.append(os.path.dirname(__file__))

from agentes.extractor import AgenteExtractor
from agentes.buscador import AgenteBuscador
from agentes.respondedor import AgenteRespondedor

# Importar configuración
try:
    import config
    print("✅ Configuración cargada")
except:
    print("⚠️  Usando configuración por defecto")
    class config:
        TAMANO_CHUNK_DEFECTO = 400
        TOP_K_DEFECTO = 3
        MOSTRAR_TIEMPO = True

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

# Variables globales para mantener el sistema cargado
sistema = {
    'listo': False,
    'extractor': None,
    'buscador': None,
    'respondedor': None,
    'documentos_cargados': 0,
    'chunks_creados': 0,
    'tiempo_carga': 0
}

@app.route('/api/status', methods=['GET'])
def status():
    """Verifica el estado del sistema"""
    return jsonify({
        'listo': sistema['listo'],
        'documentos': sistema['documentos_cargados'],
        'chunks': sistema['chunks_creados'],
        'tiempo_carga': sistema['tiempo_carga']
    })

@app.route('/api/cargar', methods=['POST'])
def cargar_documentos():
    """Carga y procesa los documentos con MAYOR PRECISIÓN"""
    inicio = time.time()
    
    try:
        data = request.json
        carpeta = data.get('carpeta', 'documentos')
        tamano_chunk = data.get('tamano_chunk', config.TAMANO_CHUNK_DEFECTO)
        
        print(f"\n{'='*60}")
        print(f"🔄 RECARGANDO SISTEMA CON PRECISIÓN MEJORADA")
        print(f"{'='*60}")
        print(f"📁 Carpeta: {carpeta}")
        print(f"✂️  Tamaño chunk: {tamano_chunk} caracteres")
        
        # Reinicializar agentes con configuración mejorada
        sistema['extractor'] = AgenteExtractor(carpeta)
        sistema['buscador'] = AgenteBuscador()
        sistema['respondedor'] = AgenteRespondedor()
        sistema['listo'] = False
        sistema['documentos_cargados'] = 0
        sistema['chunks_creados'] = 0
        
        # Procesar documentos
        print(f"\n{'─'*60}")
        documentos = sistema['extractor'].leer_documentos()
        
        if not documentos:
            return jsonify({
                'success': False,
                'error': 'No se encontraron documentos .txt o .pdf'
            }), 400
        
        # Mostrar qué archivos se cargaron
        print(f"\n📚 DOCUMENTOS ENCONTRADOS:")
        for doc in documentos:
            tipo = doc.get('tipo', 'TXT')
            tamano = len(doc['contenido'])
            print(f"   • {doc['nombre']} ({tipo}) - {tamano:,} caracteres")
        
        # Crear chunks inteligentes
        print(f"\n{'─'*60}")
        chunks = sistema['extractor'].crear_chunks(tamano_chunk)
        
        if not chunks:
            return jsonify({
                'success': False,
                'error': 'No se pudieron crear chunks de los documentos'
            }), 400
        
        # Crear base vectorial con modelo mejorado
        print(f"\n{'─'*60}")
        sistema['buscador'].crear_base_vectorial(chunks)
        
        # Actualizar estado
        sistema['listo'] = True
        sistema['documentos_cargados'] = len(documentos)
        sistema['chunks_creados'] = len(chunks)
        
        tiempo_total = time.time() - inicio
        sistema['tiempo_carga'] = tiempo_total
        
        # Crear lista de archivos cargados con detalles
        archivos_info = []
        for doc in documentos:
            tipo = doc.get('tipo', 'TXT')
            icono = '📕' if tipo == 'PDF' else '📄'
            archivos_info.append(f"{icono} {doc['nombre']} ({tipo})")
        
        print(f"\n{'='*60}")
        print(f"✅ SISTEMA LISTO EN {tiempo_total:.2f}s")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'documentos': len(documentos),
            'chunks': len(chunks),
            'archivos': archivos_info,
            'tiempo_carga': round(tiempo_total, 2),
            'mensaje': f'✅ Sistema listo! {len(documentos)} documentos procesados en {tiempo_total:.1f}s',
            'configuracion': {
                'modelo': 'Multilingüe (optimizado para español)',
                'metodo': 'Chunks inteligentes + Similitud de coseno',
                'chunks_por_doc': round(len(chunks) / len(documentos), 1)
            }
        })
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/preguntar', methods=['POST'])
def preguntar():
    """Procesa una pregunta del usuario con MAYOR PRECISIÓN"""
    inicio = time.time()
    
    try:
        if not sistema['listo']:
            return jsonify({
                'success': False,
                'error': 'Sistema no inicializado. Carga documentos primero.'
            }), 400
        
        data = request.json
        pregunta = data.get('pregunta', '')
        top_k = data.get('top_k', config.TOP_K_DEFECTO)
        tipo_respuesta = data.get('tipo_respuesta', 'precisa')  # 'precisa', 'simple', 'detallada'
        
        if not pregunta:
            return jsonify({
                'success': False,
                'error': 'Pregunta vacía'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"🔍 PROCESANDO PREGUNTA")
        print(f"{'='*60}")
        print(f"❓ Pregunta: {pregunta}")
        print(f"🎯 Top K: {top_k}")
        
        # Buscar chunks relevantes con precisión mejorada
        chunks = sistema['buscador'].buscar_relevantes(pregunta, top_k)
        
        # Generar respuesta según el tipo solicitado
        if tipo_respuesta == 'simple':
            respuesta = sistema['respondedor'].generar_respuesta_simple(pregunta, chunks)
        elif tipo_respuesta == 'detallada':
            respuesta = sistema['respondedor'].generar_respuesta_detallada(pregunta, chunks)
        else:  # 'precisa' (por defecto)
            respuesta = sistema['respondedor'].generar_respuesta_precisa(pregunta, chunks)
        
        tiempo_respuesta = time.time() - inicio
        
        # Formatear chunks para el frontend
        chunks_formateados = []
        for c in chunks:
            chunk_info = {
                'texto': c['texto'][:400] + '...' if len(c['texto']) > 400 else c['texto'],
                'fuente': c['fuente'],
                'relevancia': c.get('relevancia', 0),
                'score_semantico': c.get('score_semantico', 0),
                'score_keywords': c.get('score_keywords', 0)
            }
            chunks_formateados.append(chunk_info)
        
        # Calcular estadísticas
        if chunks:
            relevancia_promedio = sum(c.get('relevancia', 0) for c in chunks) / len(chunks)
        else:
            relevancia_promedio = 0
        
        print(f"\n⏱️  Tiempo de respuesta: {tiempo_respuesta:.2f}s")
        print(f"📊 Relevancia promedio: {relevancia_promedio:.2%}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'respuesta': respuesta,
            'chunks': chunks_formateados,
            'fuentes': list(set([c['fuente'] for c in chunks])),
            'estadisticas': {
                'tiempo_respuesta': round(tiempo_respuesta, 2),
                'chunks_encontrados': len(chunks),
                'relevancia_promedio': round(relevancia_promedio, 3),
                'relevancia_maxima': round(max([c.get('relevancia', 0) for c in chunks]) if chunks else 0, 3)
            }
        })
        
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/documentos', methods=['GET'])
def listar_documentos():
    """Lista los documentos disponibles (TXT y PDF)"""
    try:
        carpeta = request.args.get('carpeta', 'documentos')
        
        if not os.path.exists(carpeta):
            return jsonify({
                'success': True,
                'documentos': []
            })
        
        # Buscar archivos .txt y .pdf
        archivos = [f for f in os.listdir(carpeta) 
                   if f.endswith(('.txt', '.pdf'))]
        
        return jsonify({
            'success': True,
            'documentos': archivos[:20]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def obtener_config():
    """Devuelve la configuración actual del sistema"""
    try:
        return jsonify({
            'success': True,
            'configuracion': {
                'modelo_embeddings': getattr(config, 'MODELO_EMBEDDINGS', 'paraphrase-MiniLM-L6-v2'),
                'tamano_chunk_defecto': getattr(config, 'TAMANO_CHUNK_DEFECTO', 400),
                'top_k_defecto': getattr(config, 'TOP_K_DEFECTO', 3),
                'umbral_relevancia': getattr(config, 'UMBRAL_RELEVANCIA', 0.4),
                'usar_chunks_inteligentes': getattr(config, 'USAR_CHUNKS_INTELIGENTES', True),
                'usar_similitud_coseno': getattr(config, 'USAR_SIMILITUD_COSENO', True)
            }
        })
    except:
        return jsonify({
            'success': True,
            'configuracion': {
                'modelo_embeddings': 'paraphrase-MiniLM-L6-v2',
                'tamano_chunk_defecto': 400,
                'top_k_defecto': 3,
                'umbral_relevancia': 0.4,
                'usar_chunks_inteligentes': False,
                'usar_similitud_coseno': False
            }
        })

if __name__ == '__main__':
    print("="*60)
    print("🚀 INICIANDO DOCUBOT BACKEND - VERSIÓN MEJORADA")
    print("="*60)
    print("✨ Mejoras de precisión activadas:")
    print("   • Modelo multilingüe para mejor español")
    print("   • Chunks inteligentes (respetan párrafos)")
    print("   • Similitud de coseno (más precisa)")
    print("   • Reranking con keywords")
    print("   • Indicadores de confianza")
    print("="*60)
    print("📡 API disponible en: http://localhost:5000")
    print("="*60)
    print()
    app.run(debug=True, port=5000)