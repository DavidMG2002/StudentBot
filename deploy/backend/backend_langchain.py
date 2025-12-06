"""
Backend con LangChain + Gemini + BD + File Upload
NUEVO: Subida de archivos, BD SQLite, preparado para AWS S3
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import time
import os
from pathlib import Path

# Importar módulos del sistema
from sistema_langchain import SistemaMultiagenteStudentBot
from database import DatabaseManager, crear_backup

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv no instalado")

# Configuración
app = Flask(__name__)
CORS(app)

# Carpetas
UPLOAD_FOLDER = 'documentos'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear carpetas si no existen
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path('backups').mkdir(exist_ok=True)

# Sistema global
sistema_multiagente = None
db = DatabaseManager()

# API Key de Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)

def allowed_file(filename):
    """Valida extensión de archivo"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/status', methods=['GET'])
def status():
    """Estado del sistema + estadísticas de BD"""
    stats_bd = db.obtener_estadisticas_generales()
    
    if sistema_multiagente and sistema_multiagente.documentos_cargados:
        stats = sistema_multiagente.obtener_estadisticas()
        stats['gemini_habilitado'] = sistema_multiagente.agente_gemini.habilitado
        stats.update(stats_bd)
        return jsonify(stats)
    
    return jsonify({
        'listo': False,
        'documentos': 0,
        'chunks': 0,
        'gemini_habilitado': bool(GEMINI_API_KEY),
        **stats_bd
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Subida de archivos desde frontend
    NUEVO: Soporta múltiples archivos
    """
    inicio = time.time()
    
    try:
        # Validar que hay archivos
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No se enviaron archivos'
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'Archivos vacíos'
            }), 400
        
        archivos_guardados = []
        errores = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Sanitizar nombre
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Guardar archivo
                file.save(filepath)
                
                # Obtener info del archivo
                file_size = os.path.getsize(filepath)
                file_type = 'PDF' if filename.endswith('.pdf') else 'TXT'
                
                # Registrar en BD
                doc_id = db.registrar_documento(
                    nombre=filename,
                    ruta=filepath,
                    tipo=file_type,
                    tamano=file_size,
                    num_chunks=0,  # Se actualizará después
                    metodo='upload'
                )
                
                archivos_guardados.append({
                    'id': doc_id,
                    'nombre': filename,
                    'tipo': file_type,
                    'tamano': file_size
                })
                
                print(f"✓ Archivo guardado: {filename} ({file_size} bytes)")
            else:
                errores.append(f"Archivo no válido: {file.filename}")
        
        tiempo_total = time.time() - inicio
        
        return jsonify({
            'success': True,
            'archivos': archivos_guardados,
            'total': len(archivos_guardados),
            'errores': errores,
            'tiempo': round(tiempo_total, 2),
            'mensaje': f"✓ {len(archivos_guardados)} archivo(s) subido(s)"
        })
        
    except Exception as e:
        import traceback
        print(f"❌ ERROR en upload:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cargar', methods=['POST'])
def cargar_documentos():
    """Carga documentos en el sistema + actualiza BD"""
    global sistema_multiagente
    inicio = time.time()
    
    try:
        data = request.json
        carpeta = data.get('carpeta', 'documentos')
        tamano_chunk = data.get('tamano_chunk', 400)
        gemini_key = data.get('gemini_api_key', GEMINI_API_KEY)
        
        print(f"🚀 CARGANDO SISTEMA")
        print(f"📁 Carpeta: {carpeta}")
        print(f"✂️ Chunk size: {tamano_chunk}")
        print(f"🤖 Gemini: {'✓' if gemini_key else '❌'}")
        
        # Crear sistema
        sistema_multiagente = SistemaMultiagenteStudentBot(
            carpeta_documentos=carpeta,
            gemini_api_key=gemini_key
        )
        
        # Cargar documentos
        resultado = sistema_multiagente.cargar_documentos(tamano_chunk)
        
        if resultado['success']:
            # Actualizar BD con chunks
            for doc in sistema_multiagente.agente_extractor.documentos:
                # Contar chunks del documento
                chunks_doc = [c for c in sistema_multiagente.chunks 
                             if doc['nombre'] in c.get('fuente', '')]
                
                # Actualizar en BD (si ya existe)
                # En producción, harías UPDATE del num_chunks
            
            resultado['tiempo_carga'] = round(time.time() - inicio, 2)
            resultado['gemini_habilitado'] = sistema_multiagente.agente_gemini.habilitado
            resultado['mensaje'] = f"✓ Sistema listo! {resultado['documentos']} docs"
            
            print(f"✓ Sistema cargado en {resultado['tiempo_carga']}s")
            
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        import traceback
        print(f"❌ ERROR:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preguntar', methods=['POST'])
def preguntar():
    """Procesa pregunta + guarda en BD"""
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
        usar_gemini = data.get('usar_gemini', True)
        
        if not pregunta:
            return jsonify({
                'success': False,
                'error': 'Pregunta vacía'
            }), 400
        
        print(f"❓ PREGUNTA: {pregunta}")
        print(f"🔍 Top-K: {top_k}")
        print(f"🤖 Gemini: {'✓' if usar_gemini else '❌'}")
        
        # Buscar chunks
        chunks = sistema_multiagente.agente_buscador.buscar_relevantes(pregunta, top_k)
        
        # Respuesta base
        respuesta_base = sistema_multiagente.agente_respondedor.generar_respuesta(pregunta, chunks)
        
        # Mejorar con Gemini
        respuesta_final = respuesta_base
        respuesta_mejorada = False
        
        if usar_gemini and sistema_multiagente.agente_gemini.habilitado:
            print("✨ Mejorando con Gemini...")
            respuesta_final = sistema_multiagente.agente_gemini.mejorar_respuesta(
                pregunta, chunks, respuesta_base
            )
            respuesta_mejorada = True
        
        # Estadísticas
        tiempo_respuesta = time.time() - inicio
        estadisticas = {
            'tiempo_respuesta': round(tiempo_respuesta, 2),
            'chunks_encontrados': len(chunks),
            'relevancia_promedio': round(sum(c.get('relevancia', 0) for c in chunks) / len(chunks), 3) if chunks else 0,
            'gemini_usado': respuesta_mejorada
        }
        
        # GUARDAR EN BD
        conversacion_id = db.guardar_conversacion(
            pregunta=pregunta,
            respuesta=respuesta_base,
            respuesta_mejorada=respuesta_final if respuesta_mejorada else None,
            chunks=chunks,
            estadisticas=estadisticas
        )
        
        # Formatear chunks para frontend
        chunks_formateados = [{
            'texto': c['texto'][:400] + '...' if len(c['texto']) > 400 else c['texto'],
            'fuente': c['fuente'],
            'relevancia': c.get('relevancia', 0),
            'score_semantico': c.get('score_semantico', 0),
            'score_keywords': c.get('score_keywords', 0)
        } for c in chunks]
        
        print(f"✓ Respuesta generada en {tiempo_respuesta:.2f}s")
        print(f"💾 Guardado en BD (ID: {conversacion_id})")
        print("=" * 60)
        
        return jsonify({
            'success': True,
            'conversacion_id': conversacion_id,
            'respuesta': respuesta_final,
            'chunks': chunks_formateados,
            'fuentes': list(set([c['fuente'] for c in chunks])),
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        import traceback
        print(f"❌ ERROR:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/historial', methods=['GET'])
def obtener_historial():
    """Obtiene historial de conversaciones"""
    try:
        limite = request.args.get('limite', 50, type=int)
        historial = db.obtener_historial(limite=limite)
        
        return jsonify({
            'success': True,
            'historial': historial,
            'total': len(historial)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/buscar-conversaciones', methods=['GET'])
def buscar_conversaciones():
    """Busca en el historial"""
    try:
        termino = request.args.get('q', '')
        if not termino:
            return jsonify({'success': False, 'error': 'Término vacío'}), 400
        
        resultados = db.buscar_conversaciones(termino)
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total': len(resultados)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documentos', methods=['GET'])
def listar_documentos():
    """Lista documentos (de carpeta + BD)"""
    try:
        # Documentos en BD
        docs_bd = db.obtener_documentos_activos()
        
        # Documentos en carpeta
        carpeta = request.args.get('carpeta', 'documentos')
        if os.path.exists(carpeta):
            archivos = [f for f in os.listdir(carpeta) 
                       if f.endswith(('.txt', '.pdf'))]
        else:
            archivos = []
        
        return jsonify({
            'success': True,
            'documentos_bd': docs_bd,
            'documentos_carpeta': archivos[:20],
            'total_bd': len(docs_bd),
            'total_carpeta': len(archivos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/eliminar-documento/<int:doc_id>', methods=['DELETE'])
def eliminar_documento(doc_id):
    """Elimina documento de BD"""
    try:
        db.eliminar_documento(doc_id)
        return jsonify({
            'success': True,
            'mensaje': f'Documento {doc_id} eliminado'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas_generales():
    """Estadísticas del sistema"""
    try:
        stats = db.obtener_estadisticas_generales()
        return jsonify({'success': True, 'estadisticas': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup', methods=['POST'])
def crear_backup_bd():
    """Crea backup de la BD"""
    try:
        backup_path = crear_backup()
        return jsonify({
            'success': True,
            'backup': backup_path,
            'mensaje': 'Backup creado correctamente'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/resumen', methods=['POST'])
def generar_resumen():
    """Genera resumen con Gemini"""
    try:
        if not sistema_multiagente or not sistema_multiagente.documentos_cargados:
            return jsonify({
                'success': False,
                'error': 'Sistema no inicializado'
            }), 400
        
        if not sistema_multiagente.agente_gemini.habilitado:
            return jsonify({
                'success': False,
                'error': 'Gemini no habilitado'
            }), 400
        
        data = request.json
        documento_nombre = data.get('documento', '')
        
        chunks_documento = [c for c in sistema_multiagente.chunks 
                           if documento_nombre in c.get('fuente', '')]
        
        if not chunks_documento:
            return jsonify({
                'success': False,
                'error': f'Documento {documento_nombre} no encontrado'
            }), 404
        
        resumen = sistema_multiagente.agente_gemini.generar_resumen_documento(
            documento_nombre, chunks_documento
        )
        
        return jsonify({
            'success': True,
            'resumen': resumen,
            'documento': documento_nombre,
            'chunks_analizados': len(chunks_documento)
        })
        
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
            'modelo': 'gemini-2.0-flash-exp' if sistema_multiagente and sistema_multiagente.agente_gemini.habilitado else None,
            'upload_max_size': app.config['MAX_CONTENT_LENGTH'],
            'extensiones_permitidas': list(ALLOWED_EXTENSIONS)
        }
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 BACKEND LANGCHAIN + GEMINI + BD + UPLOAD")
    print("=" * 60)
    print("🌐 API: http://localhost:5000")
    print()
    print("🤖 Gemini Flash 2.0:")
    if GEMINI_API_KEY:
        print("   ✓ API Key detectada - HABILITADO")
    else:
        print("   ❌ Sin API Key - DESHABILITADO")
    print()
    print("💾 Base de Datos: SQLite (studentbot.db)")
    print("📁 Upload: Habilitado (10MB max)")
    print("=" * 60)
    
    app.run(debug=True, port=5000)