/**
 * StudentBot - Frontend JavaScript
 * Sistema de gestión de documentos con IA
 */

// ============================================
// Configuración Global
// ============================================

const API_URL = 'http://localhost:5000/api';
// Para AWS Lambda, cambiar a:
// const API_URL = 'https://tu-api-id.execute-api.us-east-1.amazonaws.com/prod/api';

let selectedFiles = [];

// ============================================
// Elementos DOM
// ============================================

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const uploadBtn = document.getElementById('uploadBtn');
const chatContainer = document.getElementById('chatContainer');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');
const loadBtn = document.getElementById('loadBtn');
const documentsList = document.getElementById('documentsList');

// ============================================
// Upload de Archivos - Drag & Drop
// ============================================

// Click en área de upload
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Drag over
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

// Drag leave
uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

// Drop
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

// Selección manual de archivos
fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

/**
 * Maneja los archivos seleccionados o arrastrados
 */
function handleFiles(files) {
    selectedFiles = Array.from(files);
    updateFileList();
    uploadBtn.style.display = selectedFiles.length > 0 ? 'block' : 'none';
}

/**
 * Actualiza la lista visual de archivos seleccionados
 */
function updateFileList() {
    fileList.innerHTML = '';
    
    selectedFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        
        const fileSize = (file.size / 1024).toFixed(1);
        const fileType = file.name.split('.').pop().toUpperCase();
        
        item.innerHTML = `
            <span>
                <strong>${fileType}</strong> ${file.name} 
                <small>(${fileSize} KB)</small>
            </span>
            <span class="remove-file" onclick="removeFile(${index})">✕</span>
        `;
        
        fileList.appendChild(item);
    });
}

/**
 * Elimina un archivo de la lista
 */
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    uploadBtn.style.display = selectedFiles.length > 0 ? 'block' : 'none';
}

/**
 * Sube los archivos seleccionados al servidor
 */
uploadBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Subiendo...';

        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showMessage('bot', `✓ ${data.total} archivo(s) subido(s) correctamente`);
            selectedFiles = [];
            updateFileList();
            uploadBtn.style.display = 'none';
            await updateStats();
            await loadDocuments();
        } else {
            showError(data.error || 'Error al subir archivos');
        }
    } catch (error) {
        console.error('Error en upload:', error);
        showError('Error al subir archivos: ' + error.message);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Subir Archivos';
    }
});

// ============================================
// Cargar Documentos
// ============================================

loadBtn.addEventListener('click', async () => {
    const folder = document.getElementById('folderInput').value;
    const chunkSize = parseInt(document.getElementById('chunkSize').value);

    try {
        loadBtn.disabled = true;
        loadBtn.textContent = 'Cargando...';
        showLoading();

        const response = await fetch(`${API_URL}/cargar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                carpeta: folder,
                tamano_chunk: chunkSize
            })
        });

        const data = await response.json();

        if (data.success) {
            questionInput.disabled = false;
            sendBtn.disabled = false;
            
            const mensaje = `✓ Sistema cargado exitosamente\n\n` +
                          `📄 ${data.documentos} documentos procesados\n` +
                          `📦 ${data.chunks} chunks creados\n` +
                          `⏱️ Tiempo: ${data.tiempo_carga}s\n` +
                          `${data.gemini_habilitado ? '✨ Gemini activo' : ''}`;
            
            showMessage('bot', mensaje);
            await updateStats();
            await loadDocuments();
        } else {
            showError(data.error || 'Error al cargar documentos');
        }
    } catch (error) {
        console.error('Error en carga:', error);
        showError('Error al cargar documentos: ' + error.message);
    } finally {
        loadBtn.disabled = false;
        loadBtn.textContent = 'Cargar Documentos';
        hideLoading();
    }
});

// ============================================
// Enviar Pregunta
// ============================================

sendBtn.addEventListener('click', () => askQuestion());

questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !sendBtn.disabled) {
        askQuestion();
    }
});

/**
 * Procesa una pregunta del usuario
 */
async function askQuestion() {
    const question = questionInput.value.trim();
    if (!question) return;

    const topK = parseInt(document.getElementById('topK').value);

    // Mostrar pregunta del usuario
    showMessage('user', question);
    questionInput.value = '';
    showLoading();

    try {
        const response = await fetch(`${API_URL}/preguntar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pregunta: question,
                top_k: topK,
                usar_gemini: true
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('bot', data.respuesta, data.chunks, data.estadisticas);
            await updateStats();
        } else {
            showError(data.error || 'Error al procesar pregunta');
        }
    } catch (error) {
        console.error('Error en pregunta:', error);
        showError('Error al procesar pregunta: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============================================
// Mostrar Mensajes en Chat
// ============================================

/**
 * Muestra un mensaje en el chat
 * @param {string} type - 'user' o 'bot'
 * @param {string} text - Texto del mensaje
 * @param {Array} chunks - Chunks relevantes (opcional)
 * @param {Object} stats - Estadísticas (opcional)
 */
function showMessage(type, text, chunks = null, stats = null) {
    const message = document.createElement('div');
    message.className = `message ${type}`;

    let content = `
        <div class="message-content">
            ${text.replace(/\n/g, '<br>')}
        </div>
        <div class="timestamp">${new Date().toLocaleTimeString()}</div>
    `;

    // Agregar chunks si existen
    if (chunks && chunks.length > 0) {
        content += `
            <div class="results-section">
                <strong>📚 Información Encontrada:</strong>
                ${chunks.map(c => `
                    <div class="chunk-item">
                        <div><strong>${c.fuente}</strong></div>
                        <div style="margin: 8px 0;">${c.texto}</div>
                        <div class="relevance-bar">
                            <div class="relevance-fill" style="width: ${c.relevancia * 100}%"></div>
                        </div>
                        <small>Relevancia: ${(c.relevancia * 100).toFixed(1)}%</small>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Agregar estadísticas si existen
    if (stats) {
        const geminiIcon = stats.gemini_usado ? '✨' : '';
        content += `
            <div class="results-section">
                <small>
                    ⏱️ Tiempo: ${stats.tiempo_respuesta}s | 
                    📊 Chunks: ${stats.chunks_encontrados} | 
                    🎯 Relevancia: ${(stats.relevancia_promedio * 100).toFixed(1)}%
                    ${stats.gemini_usado ? ' | ✨ Gemini' : ''}
                </small>
            </div>
        `;
    }

    message.innerHTML = content;
    chatContainer.appendChild(message);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Muestra indicador de carga
 */
function showLoading() {
    const loading = document.createElement('div');
    loading.className = 'loading';
    loading.id = 'loading';
    loading.innerHTML = `
        <div class="spinner"></div>
        <p>Procesando...</p>
    `;
    chatContainer.appendChild(loading);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Oculta indicador de carga
 */
function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.remove();
    }
}

/**
 * Muestra mensaje de error
 */
function showError(message) {
    const error = document.createElement('div');
    error.className = 'error';
    error.textContent = '❌ ' + message;
    chatContainer.appendChild(error);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Muestra mensaje de éxito
 */
function showSuccess(message) {
    const success = document.createElement('div');
    success.className = 'success';
    success.textContent = '✓ ' + message;
    chatContainer.appendChild(success);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ============================================
// Actualizar Estadísticas
// ============================================

/**
 * Actualiza las estadísticas del sistema
 */
async function updateStats() {
    try {
        const response = await fetch(`${API_URL}/status`);
        const data = await response.json();

        document.getElementById('statDocs').textContent = data.documentos || 0;
        document.getElementById('statChunks').textContent = data.chunks || 0;
        document.getElementById('statConv').textContent = data.total_conversaciones || 0;
    } catch (error) {
        console.error('Error al actualizar estadísticas:', error);
    }
}

/**
 * Carga la lista de documentos
 */
async function loadDocuments() {
    try {
        const response = await fetch(`${API_URL}/documentos`);
        const data = await response.json();

        const docsList = document.getElementById('documentsList');
        
        if (data.success && data.documentos_bd && data.documentos_bd.length > 0) {
            docsList.innerHTML = data.documentos_bd.map(doc => `
                <div class="doc-item">
                    <span>${doc.nombre}</span>
                    <span class="doc-badge ${doc.tipo.toLowerCase()}">${doc.tipo}</span>
                </div>
            `).join('');
        } else if (data.documentos_carpeta && data.documentos_carpeta.length > 0) {
            docsList.innerHTML = data.documentos_carpeta.map(nombre => {
                const tipo = nombre.endsWith('.pdf') ? 'PDF' : 'TXT';
                return `
                    <div class="doc-item">
                        <span>${nombre}</span>
                        <span class="doc-badge ${tipo.toLowerCase()}">${tipo}</span>
                    </div>
                `;
            }).join('');
        } else {
            docsList.innerHTML = '<p style="color: #999; text-align: center;">No hay documentos</p>';
        }
    } catch (error) {
        console.error('Error al cargar documentos:', error);
    }
}

// ============================================
// Sliders de Configuración
// ============================================

document.getElementById('chunkSize').addEventListener('input', (e) => {
    document.getElementById('chunkValue').textContent = e.target.value;
});

document.getElementById('topK').addEventListener('input', (e) => {
    document.getElementById('topKValue').textContent = e.target.value;
});

// ============================================
// Inicialización
// ============================================

/**
 * Inicializa la aplicación
 */
async function init() {
    console.log('StudentBot iniciando...');
    console.log('API URL:', API_URL);
    
    // Cargar estadísticas iniciales
    await updateStats();
    await loadDocuments();
    
    // Verificar estado del backend
    try {
        const response = await fetch(`${API_URL}/status`);
        const data = await response.json();
        
        if (data.listo) {
            console.log('✓ Backend conectado');
            questionInput.disabled = false;
            sendBtn.disabled = false;
        } else {
            console.log('⚠️ Backend disponible pero sin documentos cargados');
        }
    } catch (error) {
        console.error('❌ Error al conectar con backend:', error);
        showError('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
    }
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', init);

// ============================================
// Utilidades
// ============================================

/**
 * Formatea bytes a KB/MB
 */
function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Valida el formato de archivo
 */
function isValidFile(filename) {
    const validExtensions = ['.txt', '.pdf'];
    return validExtensions.some(ext => filename.toLowerCase().endsWith(ext));
}

/**
 * Limpia el chat
 */
function clearChat() {
    chatContainer.innerHTML = `
        <div class="welcome">
            <h1>🤖 StudentBot</h1>
            <p>Asistente inteligente de documentos<br>
            <span class="gemini-badge">✨ Potenciado por Gemini Flash 2.5</span></p>
            <p style="margin-top: 20px; color: #999;">Carga tus documentos y hazme preguntas</p>
        </div>
    `;
}

// Exponer funciones al scope global (para onclick en HTML)
window.removeFile = removeFile;
window.clearChat = clearChat;