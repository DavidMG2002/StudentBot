"""
Backend con LangChain - Nueva versión
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from sistema_langchain import SistemaMultiagenteDocuBot

app = Flask(__name__)
CORS(app)

# Sistema global
sistema_multiagente = None

@app.route('/api/status', methods=['GET'])
def status():
    if sistema_multiagente and sistema_multiagente.documentos_cargados:
        stats = sistema_multiagente.obtener_estadisticas()
        return jsonify(stats)
    return jsonify({'listo': False, 'documentos': 0, 'chunks': 0})

@app.route('/api/cargar', methods=['POST'])
def cargar_documentos():
    global sistema_multiagente
    inicio = time.time()
    
    try:
        data = request.json
        carpeta = data.get('carpeta', 'documentos')
        tamano_chunk = data.get('tamano_chunk', 400)
        
        # Crear sistema LangChain
        sistema_multiagente = SistemaMultiagenteDocuBot(carpeta)
        
        # Cargar documentos
        resultado = sistema_multiagente.cargar_documentos(tamano_chunk)
        
        if resultado['success']:
            resultado['tiempo_carga'] = round(time.time() - inicio, 2)
            resultado['mensaje'] = f"✅ Sistema LangChain listo! {resultado['documentos']} docs"
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preguntar', methods=['POST'])
def preguntar():
    inicio = time.time()
    
    try:
        if not sistema_multiagente or not sistema_multiagente.documentos_cargados:
            return jsonify({
                'success': False,
                'error': 'Sistema no inicializado'
            }), 400
        
        data = request.json
        pregunta = data.get('pregunta', '')
        top_k = data.get('top_k', 3)
        
        # Procesar con LangChain
        chunks = sistema_multiagente.agente_buscador.buscar_relevantes(pregunta, top_k)
        respuesta = sistema_multiagente.agente_respondedor.generar_respuesta(pregunta, chunks)
        
        chunks_formateados = [{
            'texto': c['texto'][:400] + '...' if len(c['texto']) > 400 else c['texto'],
            'fuente': c['fuente'],
            'relevancia': c.get('relevancia', 0)
        } for c in chunks]
        
        return jsonify({
            'success': True,
            'respuesta': respuesta,
            'chunks': chunks_formateados,
            'fuentes': list(set([c['fuente'] for c in chunks])),
            'tiempo_respuesta': round(time.time() - inicio, 2)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/documentos', methods=['GET'])
def listar_documentos():
    import os
    try:
        carpeta = request.args.get('carpeta', 'documentos')
        if not os.path.exists(carpeta):
            return jsonify({'success': True, 'documentos': []})
        
        archivos = [f for f in os.listdir(carpeta) if f.endswith(('.txt', '.pdf'))]
        return jsonify({'success': True, 'documentos': archivos[:20]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 BACKEND LANGCHAIN - DocuBot")
    print("="*60)
    print("✨ Sistema Multiagente LangChain")
    print("📡 API: http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=5000)