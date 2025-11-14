// Configuración de la API
const API_URL = 'http://localhost:5000/api';

// Referencias a elementos del DOM
const elements = {
    statusBar: document.getElementById('statusBar'),
    statusIcon: document.getElementById('statusIcon'),
    statusText: document.getElementById('statusText'),
    docCount: document.getElementById('docCount'),
    carpeta: document.getElementById('carpeta'),
    tamanoChunk: document.getElementById('tamanoChunk'),
    tamanoChunkValue: document.getElementById('tamanoChunkValue'),
    topK: document.getElementById('topK'),
    topKValue: document.getElementById('topKValue'),
    btnCargar: document.getElementById('btnCargar'),
    btnRefrescar: document.getElementById('btnRefrescar'),
    loadingCargar: document.getElementById('loadingCargar'),
    cargarInfo: document.getElementById('cargarInfo'),
    listaDocumentos: document.getElementById('listaDocumentos'),
    chatMessages: document.getElementById('chatMessages'),
    inputPregunta: document.getElementById('inputPregunta'),
    btnPreguntar: document.getElementById('btnPreguntar'),
    loadingPregunta: document.getElementById('loadingPregunta'),
    chunksContainer: document.getElementById('chunksContainer'),
    chunksContent: document.getElementById('chunksContent'),
    statTxt: document.getElementById('statTxt'),
    statPdf: document.getElementById('statPdf'),
    statChunks: document.getElementById('statChunks')
};

// Estado del sistema
let sistemaCargado = false;

// Inicializar la aplicación
function init() {
    console.log('🚀 Iniciando DocuBot Frontend...');
    
    // Event listeners para sliders
    elements.tamanoChunk.addEventListener('input', (e) => {
        elements.tamanoChunkValue.textContent = e.target.value;
    });

    elements.topK.addEventListener('input', (e) => {
        elements.topKValue.textContent = e.target.value;
    });

    // Event listeners para botones
    elements.btnCargar.addEventListener('click', cargarDocumentos);
    elements.btnRefrescar.addEventListener('click', listarDocumentos);
    elements.btnPreguntar.addEventListener('click', enviarPregunta);
    
    elements.inputPregunta.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !elements.btnPreguntar.disabled) {
            enviarPregunta();
        }
    });

    // Cargar lista de documentos inicial
    listarDocumentos();

    // Verificar estado del sistema
    verificarEstado();
    
    console.log('✅ Frontend inicializado');
}

// Verificar estado del backend
async function verificarEstado() {
    try {
        const response = await fetch(`${API_URL}/status`);
        const data = await response.json();

        if (data.listo) {
            actualizarEstado(true, 'Sistema activo y listo', data.documentos);
            if (data.chunks) {
                elements.statChunks.textContent = data.chunks;
            }
        } else {
            actualizarEstado(false, 'Sistema no inicializado - Carga documentos primero', 0);
        }
    } catch (error) {
        console.log('⚠️ Backend no disponible:', error.message);
        actualizarEstado(false, '❌ Backend no disponible - Ejecuta: python backend.py', 0);
    }
}

// Actualizar barra de estado
function actualizarEstado(listo, mensaje, numDocs = 0) {
    sistemaCargado = listo;
    
    if (listo) {
        elements.statusBar.className = 'status-bar success';
        elements.statusIcon.textContent = '✅';
        elements.inputPregunta.disabled = false;
        elements.btnPreguntar.disabled = false;
        elements.inputPregunta.placeholder = 'Escribe tu pregunta aquí... (Presiona Enter)';
    } else {
        elements.statusBar.className = 'status-bar';
        elements.statusIcon.textContent = '⚠️';
        elements.inputPregunta.disabled = true;
        elements.btnPreguntar.disabled = true;
        elements.inputPregunta.placeholder = 'Carga documentos primero...';
    }
    
    elements.statusText.textContent = mensaje;
    elements.docCount.textContent = `${numDocs} documento${numDocs !== 1 ? 's' : ''}`;
}

// Listar documentos disponibles
async function listarDocumentos() {
    console.log('📁 Listando documentos...');
    
    try {
        const carpeta = elements.carpeta.value;
        const response = await fetch(`${API_URL}/documentos?carpeta=${carpeta}`);
        const data = await response.json();

        if (data.success && data.documentos.length > 0) {
            const txtDocs = data.documentos.filter(d => d.endsWith('.txt'));
            const pdfDocs = data.documentos.filter(d => d.endsWith('.pdf'));
            
            elements.statTxt.textContent = txtDocs.length;
            elements.statPdf.textContent = pdfDocs.length;
            
            let html = '';
            
            if (pdfDocs.length > 0) {
                html += '<div class="doc-section"><strong>📕 PDFs:</strong></div>';
                pdfDocs.forEach(doc => {
                    html += `<div class="documento-item pdf">📕 ${doc}</div>`;
                });
            }
            
            if (txtDocs.length > 0) {
                html += '<div class="doc-section"><strong>📄 TXT:</strong></div>';
                txtDocs.forEach(doc => {
                    html += `<div class="documento-item txt">📄 ${doc}</div>`;
                });
            }
            
            elements.listaDocumentos.innerHTML = html;
            console.log(`✅ ${data.documentos.length} documentos encontrados`);
        } else {
            elements.listaDocumentos.innerHTML = `
                <p class="text-muted">📂 No hay documentos en la carpeta</p>
                <p class="text-muted" style="font-size: 12px;">Agrega archivos .txt o .pdf</p>
            `;
            elements.statTxt.textContent = '0';
            elements.statPdf.textContent = '0';
        }
    } catch (error) {
        console.error('❌ Error al listar documentos:', error);
        elements.listaDocumentos.innerHTML = '<p class="text-muted">❌ Error al cargar lista</p>';
    }
}

// Cargar documentos en el sistema
async function cargarDocumentos() {
    console.log('🔄 Iniciando carga de documentos...');
    
    try {
        elements.btnCargar.disabled = true;
        elements.loadingCargar.style.display = 'flex';
        elements.cargarInfo.style.display = 'none';

        const payload = {
            carpeta: elements.carpeta.value,
            tamano_chunk: parseInt(elements.tamanoChunk.value)
        };

        const response = await fetch(`${API_URL}/cargar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            actualizarEstado(true, `✅ ${data.documentos} documentos procesados`, data.documentos);
            
            elements.statChunks.textContent = data.chunks;
            
            elements.cargarInfo.style.display = 'block';
            elements.cargarInfo.className = 'info-box success';
            elements.cargarInfo.innerHTML = `
                <strong>🎉 Sistema listo!</strong><br>
                📚 Documentos: ${data.documentos}<br>
                ✂️ Chunks: ${data.chunks}<br>
                ${data.gemini_habilitado ? '💎 Gemini: Habilitado' : '⚠️ Gemini: Deshabilitado'}
            `;
            
            agregarMensajeBot(`
                🎉 <strong>¡Sistema cargado exitosamente!</strong><br><br>
                📊 <strong>Resumen:</strong><br>
                • ${data.documentos} documentos procesados<br>
                • ${data.chunks} chunks creados<br>
                ${data.gemini_habilitado ? '• 💎 Gemini Flash activo<br>' : ''}
                <br>✅ Ya puedes hacer preguntas!
            `);
            
            listarDocumentos();
        } else {
            mostrarError(data.error);
            elements.cargarInfo.style.display = 'block';
            elements.cargarInfo.className = 'info-box error';
            elements.cargarInfo.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
        }
    } catch (error) {
        console.error('❌ Error al cargar documentos:', error);
        mostrarError('Error de conexión. Verifica que el backend esté ejecutándose.');
        elements.cargarInfo.style.display = 'block';
        elements.cargarInfo.className = 'info-box error';
        elements.cargarInfo.innerHTML = `
            <strong>❌ Error de conexión</strong><br>
            Ejecuta: <code>python backend.py</code>
        `;
    } finally {
        elements.btnCargar.disabled = false;
        elements.loadingCargar.style.display = 'none';
    }
}

// Enviar pregunta
async function enviarPregunta() {
    const pregunta = elements.inputPregunta.value.trim();

    if (!pregunta) return;

    try {
        agregarMensajeUsuario(pregunta);
        elements.inputPregunta.value = '';
        elements.inputPregunta.disabled = true;
        elements.btnPreguntar.disabled = true;
        elements.loadingPregunta.style.display = 'flex';
        elements.chunksContainer.style.display = 'none';

        const response = await fetch(`${API_URL}/preguntar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pregunta: pregunta,
                top_k: parseInt(elements.topK.value),
                usar_gemini: true
            })
        });

        const data = await response.json();

        if (data.success) {
            // Mostrar chunks
            if (data.chunks && data.chunks.length > 0) {
                mostrarChunks(data.chunks);
            }

            // Mostrar respuesta mejorada por Gemini
            if (data.respuesta) {
                const geminiUsado = data.estadisticas?.gemini_usado || false;
                agregarMensajeBotGemini(data.respuesta, geminiUsado);
                
                if (geminiUsado && data.estadisticas?.tiempo_respuesta) {
                    agregarIndicadorGemini(data.estadisticas.tiempo_respuesta);
                }
            }
        } else {
            mostrarError(data.error);
        }
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarError('Error al procesar la pregunta');
    } finally {
        elements.inputPregunta.disabled = false;
        elements.btnPreguntar.disabled = false;
        elements.loadingPregunta.style.display = 'none';
        elements.inputPregunta.focus();
    }
}

// Mostrar chunks relevantes
function mostrarChunks(chunks) {
    elements.chunksContent.innerHTML = chunks.map((chunk, index) => {
        const tipo = chunk.fuente.includes('PDF') ? 'pdf' : 'txt';
        const icono = tipo === 'pdf' ? '📕' : '📄';
        const relevancia = (chunk.relevancia * 100).toFixed(0);
        
        return `
            <div class="chunk-item ${tipo}">
                <div class="chunk-header">
                    ${icono} <strong>Fragmento ${index + 1}</strong> - ${chunk.fuente}
                    <span class="chunk-relevancia">${relevancia}%</span>
                </div>
                <div class="chunk-text">${chunk.texto}</div>
            </div>
        `;
    }).join('');

    elements.chunksContainer.style.display = 'block';
}

// Agregar mensaje del bot mejorado por Gemini
function agregarMensajeBotGemini(texto, geminiUsado = false) {
    const mensaje = document.createElement('div');
    mensaje.className = 'message bot';
    const timestamp = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    
    const badgeGemini = geminiUsado ? '<span class="badge gemini-badge">💎 Gemini Flash</span>' : '';
    
    mensaje.innerHTML = `
        <div class="message-header">
            <span class="avatar">🤖</span>
            <strong>DocuBot</strong>
            ${badgeGemini}
            <span class="timestamp">${timestamp}</span>
        </div>
        <div class="message-content ${geminiUsado ? 'gemini-response' : ''}">${texto.replace(/\n/g, '<br>')}</div>
    `;
    elements.chatMessages.appendChild(mensaje);
    scrollToBottom();
}

// Indicador de Gemini
function agregarIndicadorGemini(tiempo) {
    const indicador = document.createElement('div');
    indicador.className = 'gemini-indicator';
    indicador.innerHTML = `💎 Respuesta mejorada con Gemini Flash (${tiempo}s)`;
    elements.chatMessages.appendChild(indicador);
    scrollToBottom();
}

// Agregar mensaje del bot
function agregarMensajeBot(texto) {
    agregarMensajeBotGemini(texto, false);
}

// Agregar mensaje del usuario
function agregarMensajeUsuario(texto) {
    const mensaje = document.createElement('div');
    mensaje.className = 'message user';
    const timestamp = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    mensaje.innerHTML = `
        <div class="message-header">
            <span class="avatar">👤</span>
            <strong>Tú</strong>
            <span class="timestamp">${timestamp}</span>
        </div>
        <div class="message-content">${texto}</div>
    `;
    elements.chatMessages.appendChild(mensaje);
    scrollToBottom();
}

// Mostrar error
function mostrarError(mensaje) {
    agregarMensajeBot(`❌ <strong>Error:</strong> ${mensaje}`);
}

// Scroll al final del chat
function scrollToBottom() {
    setTimeout(() => {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }, 100);
}

// Inicializar cuando cargue la página
document.addEventListener('DOMContentLoaded', init);