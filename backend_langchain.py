"""
Backend con LangChain + Gemini Flash 2.0
API REST para StudentBot con mejoras de IA
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import os
from sistema_langchain import SistemaMultiagenteStudentBot
                                       
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("|X| python-dotenv no instalado, usando variables de entorno del sistema")

from sistema_langchain import SistemaMultiagenteStudentBot

app = Flask(__name__)             
CORS(app)
# Sistema global
sistema_multiagente = None

# API Key de Gemini (leer de variable de entorno o archivo)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)

@app.route('/api/status', methods=['GET'])
def status():
    """Estado del sistema"""
    if sistema_multiagente and sistema_multiagente.documentos_cargados:
        stats = sistema_multiagente.obtener_estadisticas()
        stats['gemini_habilitado'] = sistema_multiagente.agente_gemini.habilitado
        return jsonify(stats)
    return jsonify({
        'listo': False, 
        'documentos': 0, 
        'chunks': 0,
        'gemini_habilitado': bool(GEMINI_API_KEY)
    })

@app.route('/api/cargar', methods=['POST'])
def cargar_documentos():
    """Carga documentos en el sistema"""
    global sistema_multiagente
    inicio = time.time()
    
    try:
        data = request.json
        carpeta = data.get('carpeta', 'documentos')
        tamano_chunk = data.get('tamano_chunk', 400)
        gemini_key = data.get('gemini_api_key', GEMINI_API_KEY)
        
        
        print(f" CARGANDO SISTEMA")

        print(f"Carpeta: {carpeta}")
        print(f"Chunk size: {tamano_chunk}")
        print(f"Gemini: {'✓ Habilitado' if gemini_key else '|X| Deshabilitado'}")
        
        # Crear sistema LangChain con Gemini
        sistema_multiagente = SistemaMultiagenteStudentBot(
            carpeta_documentos=carpeta,
            gemini_api_key=gemini_key
        )
        
        # Cargar documentos
        resultado = sistema_multiagente.cargar_documentos(tamano_chunk)
        
        if resultado['success']:
            resultado['tiempo_carga'] = round(time.time() - inicio, 2)
            resultado['gemini_habilitado'] = sistema_multiagente.agente_gemini.habilitado
            resultado['mensaje'] = f"✓ Sistema LangChain + Gemini listo! {resultado['documentos']} docs"
            
            print(f"✓ Sistema cargado en {resultado['tiempo_carga']}s")
            
            
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        import traceback
        print(f"|X| ERROR:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preguntar', methods=['POST'])
def preguntar():
    """Procesa una pregunta del usuario"""
    inicio = time.time()
    
    try:
        if not sistema_multiagente or not sistema_multiagente.documentos_cargados:
            return jsonify({
                'success': False,
                'error': 'Sistema no inicializado. Carga documentos primero.'
            }), 400
        
        data = request.json
        pregunta = data.get('pregunta', '')
        top_k = data.get('top_k', 3)
        usar_gemini = data.get('usar_gemini', True)  # Por defecto activado
        
        if not pregunta:
            return jsonify({
                'success': False,
                'error': 'Pregunta vacía'
            }), 400
        
       
        print(f"? PREGUNTA: {pregunta}")
        print(f"🔍 Top-K: {top_k}")
        print(f" Gemini: {'✓ Activado' if usar_gemini else '|X| Desactivado'}")
       
        
        # Buscar chunks relevantes
        chunks = sistema_multiagente.agente_buscador.buscar_relevantes(pregunta, top_k)
        
        # Generar respuesta base
        respuesta_base = sistema_multiagente.agente_respondedor.generar_respuesta(pregunta, chunks)
        
        # Mejorar con Gemini si está habilitado
        if usar_gemini and sistema_multiagente.agente_gemini.habilitado:
            print("✓✓ Mejorando respuesta con Gemini...")
            respuesta_final = sistema_multiagente.agente_gemini.mejorar_respuesta(
                pregunta,
                chunks,
                respuesta_base
            )
            respuesta_mejorada = True
        else:
            respuesta_final = respuesta_base
            respuesta_mejorada = False
        
        # Formatear chunks para frontend
        chunks_formateados = [{
            'texto': c['texto'][:400] + '...' if len(c['texto']) > 400 else c['texto'],
            'fuente': c['fuente'],
            'relevancia': c.get('relevancia', 0),
            'score_semantico': c.get('score_semantico', 0),
            'score_keywords': c.get('score_keywords', 0)
        } for c in chunks]
        
        tiempo_respuesta = time.time() - inicio
        
        print(f"\n✓ Respuesta generada en {tiempo_respuesta:.2f}s")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'respuesta': respuesta_final,
            'chunks': chunks_formateados,
            'fuentes': list(set([c['fuente'] for c in chunks])),
            'estadisticas': {
                'tiempo_respuesta': round(tiempo_respuesta, 2),
                'chunks_encontrados': len(chunks),
                'relevancia_promedio': round(sum(c.get('relevancia', 0) for c in chunks) / len(chunks), 3) if chunks else 0,
                'gemini_usado': respuesta_mejorada
            }
        })
        
    except Exception as e:
        import traceback
        print(f"|X| ERROR:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/resumen', methods=['POST'])
def generar_resumen():
    """Genera resumen de un documento con Gemini"""
    try:
        if not sistema_multiagente or not sistema_multiagente.documentos_cargados:
            return jsonify({
                'success': False,
                'error': 'Sistema no inicializado'
            }), 400
        
        if not sistema_multiagente.agente_gemini.habilitado:
            return jsonify({
                'success': False,
                'error': 'Gemini no está habilitado. Proporciona API key.'
            }), 400
        
        data = request.json
        documento_nombre = data.get('documento', '')
        
        # Obtener chunks del documento
        chunks_documento = [c for c in sistema_multiagente.chunks 
                           if documento_nombre in c.get('fuente', '')]
        
        if not chunks_documento:
            return jsonify({
                'success': False,
                'error': f'Documento {documento_nombre} no encontrado'
            }), 404
        
        # Generar resumen con Gemini
        resumen = sistema_multiagente.agente_gemini.generar_resumen_documento(
            documento_nombre,
            chunks_documento
        )
        
        return jsonify({
            'success': True,
            'resumen': resumen,
            'documento': documento_nombre,
            'chunks_analizados': len(chunks_documento)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documentos', methods=['GET'])
def listar_documentos():
    """Lista documentos disponibles"""
    try:
        carpeta = request.args.get('carpeta', 'documentos')
        if not os.path.exists(carpeta):
            return jsonify({'success': True, 'documentos': []})
        
        archivos = [f for f in os.listdir(carpeta) if f.endswith(('.txt', '.pdf'))]
        return jsonify({'success': True, 'documentos': archivos[:20]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['GET'])
def obtener_config():
    """Configuración actual"""
    return jsonify({
        'success': True,
        'configuracion': {
            'gemini_disponible': bool(GEMINI_API_KEY),
            'gemini_habilitado': sistema_multiagente.agente_gemini.habilitado if sistema_multiagente else False,
            'modelo': 'gemini-2.0-flash-exp' if sistema_multiagente and sistema_multiagente.agente_gemini.habilitado else None
        }
    })

if __name__ == '__main__':
    print("BACKEND LANGCHAIN + GEMINI FLASH 2.0")
    print("✓✓ Sistema Multiagente Mejorado")
    print("0.< API: http://localhost:5000")
    print()
    print("✓ Gemini Flash 2.0:")
    if GEMINI_API_KEY:
        print("   ✓ API Key detectada - Gemini HABILITADO")
        print("   ✓✓ Respuestas mejoradas con IA")
    else:
        print("   |X| Sin API Key - Gemini DESHABILITADO")
        print("    o-  Para habilitar: export GEMINI_API_KEY='tu-key'")
        print("    o-  O agregar en código: GEMINI_API_KEY = 'tu-key'")
    print()
    app.run(debug=True, port=5000)