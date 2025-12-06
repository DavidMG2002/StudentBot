# StudentBot – Sistema Multi-Agente de Análisis de Documentos

Sistema inteligente para procesamiento y análisis de documentos (TXT y PDF) mediante agentes especializados, búsqueda vectorial, OCR y generación de respuestas con IA.

---

## Pila Tecnológica

### Backend:

- Python 3.10+
- LangChain (Gestión de agentes y cadenas)
- FAISS (Vectorial base)
- Google Gemini Flash 2.0 (Mejora de respuestas)
- Flask (API REST)
- OCR Tesseract (opcional)
- SQLite (Base de datos)

### Frontend:

- HTML, CSS, JavaScript
- Servidor simple con http.server (modo local)

---

## Características

- 4 agentes especializados (Extractor, Buscador, Respondedor, Mejorador)
- Procesamiento de documentos TXT y PDF (incluye OCR)
- Búsqueda semántica mediante incrustaciones multilingües
- Sistema de puntuación y nivel de confianza en respuestas
- Mejoras de lenguaje natural con Gemini Flash 2.0
- Arquitectura modular y escalable
- API REST + Interfaz Web Simple
- Soporte para análisis conversacional
- **☁️ Despliegue en AWS soportado**

---

## Arquitectura Multi-Agente

### 1. Agente Extractor

- Lee documentos TXT y PDF
- Aplica OCR en PDFs escaneados
- Genera trozos inteligentes
- Extrae metadatos útiles

### 2. Agente Buscador

- Convierte los trozos en incrustaciones
- Almacena vectores en FAISS
- Calcula similitud de coseno
- Reordena resultados por palabras clave

### 3. Agente Respondedor

- Genera respuestas contextuales
- Añade nivel de confianza (Muy Alta, Alta, Media, Baja)
- Incluye citas y fuentes del documento

### 4. Agente Mejorador (Gemini)

- Reescribe las respuestas
- Mejora la claridad, coherencia y naturalidad
- Genera resúmenes ejecutivos y explicaciones más limpias

---

## Instalación Local

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd studentbot
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. (Opcional) Instalar Tesseract para OCR

**Windows:**
```
https://github.com/UB-Mannheim/tesseract/wiki
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

**Mac:**
```bash
brew install tesseract tesseract-lang
```

### 5. Configurar clave de Gemini (opcional)

Crear archivo `.env`:

```
GEMINI_API_KEY=tu_api_key
```

---

## Uso

### Modo API REST

Iniciar el backend:

```bash
python backend_langchain.py
```

El servidor estará disponible en: **http://localhost:5000**

#### Cargar documentos

```http
POST /api/cargar
{
  "carpeta": "documentos",
  "tamano_chunk": 400
}
```

#### Hacer una pregunta

```http
POST /api/preguntar
{
  "pregunta": "¿Qué es el emprendimiento?",
  "top_k": 3,
  "usar_gemini": true
}
```

#### Generar resumen

```http
POST /api/resumen
{
  "documento": "archivo.pdf"
}
```

### Modo Interfaz Web

```bash
cd frontend
python -m http.server 8000
```

Abrir en: **http://localhost:8000**

### Modo Script

```python
from sistema_langchain import SistemaMultiagenteStudentBot

sistema = SistemaMultiagenteStudentBot(
    carpeta_documentos="documentos",
    gemini_api_key="tu_key"
)

resultado = sistema.cargar_documentos(tamano_chunk=400)
print(resultado)

respuesta = sistema.procesar_pregunta("¿Qué es el emprendimiento?")
print(respuesta)
```

---

## ☁️ Despliegue en AWS

Este proyecto está completamente preparado para desplegarse en Amazon Web Services (AWS).

### Arquitectura AWS Implementada

```
┌─────────────────────────────────────────────────────────┐
│                    USUARIO                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  EC2 Instance         │
         │  Ubuntu 22.04 LTS     │
         │  • Backend (Flask)    │
         │  • Frontend (NGINX)   │
         │  • Base de Datos      │
         └───────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌──────┐    ┌──────┐    ┌──────┐
    │  S3  │    │ IAM  │    │Cloud │
    │(Docs)│    │(Roles)│   │Watch │
    └──────┘    └──────┘    └──────┘
```

### Servicios AWS Utilizados

- **EC2**: Servidor de backend (Ubuntu 22.04 LTS, t3.micro)
- **S3**: Almacenamiento de documentos (opcional)
- **IAM**: Gestión de permisos y roles
- **CloudWatch**: Monitoreo y logs
- **VPC**: Red privada virtual
- **Security Groups**: Firewall (puertos 22, 80, 5000)

### Despliegue Rápido en EC2

#### 1. Crear instancia EC2

**Configuración:**
- **Tipo**: t3.micro (Free tier eligible)
- **SO**: Ubuntu Server 22.04 LTS
- **Almacenamiento**: 20 GB gp3
- **Security Groups**: 
  - SSH (22)
  - HTTP (80)
  - Custom TCP (5000)

#### 2. Conectar a la instancia

```bash
ssh -i studentbot-key.pem ubuntu@TU-IP-PUBLICA
```

O usar **EC2 Instance Connect** desde la consola de AWS.

#### 3. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.10 python3.10-venv python3-pip nginx git
```

#### 4. Configurar el proyecto

```bash
# Crear directorio
mkdir studentbot
cd studentbot

# Crear entorno virtual
python3.10 -m venv venv
source venv/bin/activate

# Subir archivos (usar SCP o crear manualmente)
# O clonar desde repositorio:
# git clone <tu-repo> .

# Instalar dependencias Python
pip install -r requirements.txt
```

#### 5. Configurar variables de entorno

```bash
nano .env
```

Agregar:
```
GEMINI_API_KEY=tu_api_key_aqui
```

#### 6. Probar el backend

```bash
python backend_langchain.py
```

Acceder desde: `http://TU-IP-PUBLICA:5000/api/status`

#### 7. Configurar NGINX (Producción)

```bash
sudo nano /etc/nginx/sites-available/studentbot
```

Contenido:
```nginx
server {
    listen 80;
    server_name TU-IP-PUBLICA;

    # Frontend
    location / {
        root /home/ubuntu/studentbot/frontend;
        index index.html;
        try_files $uri $uri/ =404;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Activar configuración:
```bash
sudo ln -s /etc/nginx/sites-available/studentbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. Configurar servicio systemd (Ejecutar en background)

```bash
sudo nano /etc/systemd/system/studentbot.service
```

Contenido:
```ini
[Unit]
Description=StudentBot Backend Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/studentbot
Environment="PATH=/home/ubuntu/studentbot/venv/bin"
Environment="GEMINI_API_KEY=tu_api_key"
ExecStart=/home/ubuntu/studentbot/venv/bin/python backend_langchain.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl enable studentbot
sudo systemctl start studentbot
sudo systemctl status studentbot
```

### URLs de Acceso

Una vez desplegado:

- **Frontend**: `http://TU-IP-PUBLICA/`
- **API Status**: `http://TU-IP-PUBLICA/api/status`
- **API Cargar**: `http://TU-IP-PUBLICA/api/cargar`
- **API Preguntar**: `http://TU-IP-PUBLICA/api/preguntar`

### Costos Estimados (Tier Gratuito)

| Servicio | Uso | Costo Mensual |
|----------|-----|---------------|
| EC2 t3.micro | 750 horas/mes | $0 (12 meses free) |
| EBS 20GB | Almacenamiento | $0 (30 GB free) |
| S3 (opcional) | 5 GB | ~$0.12 |
| Data Transfer | 15 GB salida | $0 (free tier) |
| **TOTAL** | | **~$0-0.12/mes** |

**Nota:** Después del tier gratuito: ~$8-10/mes

### Monitoreo y Logs

**Ver logs del servicio:**
```bash
sudo journalctl -u studentbot -f
```

**Ver logs de NGINX:**
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

**Ver métricas en CloudWatch:**
- CPU, memoria, red
- Logs de aplicación (si configuras CloudWatch Agent)

### Actualizar la Aplicación

```bash
cd /home/ubuntu/studentbot
git pull  # Si usas Git
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart studentbot
```

### Seguridad en AWS

**Recomendaciones:**
- ✅ Usar claves SSH fuertes
- ✅ Actualizar Security Groups solo con IPs necesarias
- ✅ Configurar backups automáticos de EBS
- ✅ Usar HTTPS con certificado SSL (Let's Encrypt)
- ✅ Configurar IAM roles con permisos mínimos
- ✅ Habilitar CloudWatch Alarms

### Habilitar HTTPS (Opcional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

---

## Estructura del Proyecto

```
studentbot/
├── agentes/
│   ├── __init__.py
│   ├── extractor_langchain.py
│   ├── buscador_langchain.py
│   ├── respondedor_langchain.py
│   └── mejorador_respuestas.py
├── documentos/
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── backups/
├── deploy/                    # Archivos para AWS
│   ├── backend/
│   └── frontend/
├── sistema_langchain.py
├── backend_langchain.py
├── database.py
├── config.py
├── requirements.txt
├── .env                       # Variables de entorno
├── studentbot.db              # Base de datos SQLite
└── README.md
```

---

## Solución de Problemas

### OCR no disponible

```bash
pip install pytesseract pdf2image Pillow
```

### FAISS no instalado

```bash
pip install faiss-cpu
```

### Error con Gemini

- Revisar variable `GEMINI_API_KEY` en `.env`
- El sistema puede funcionar sin Gemini

### Backend no arranca en EC2

```bash
# Ver logs
sudo journalctl -u studentbot -n 50

# Verificar puerto
sudo netstat -tulpn | grep 5000

# Revisar permisos
ls -la /home/ubuntu/studentbot
```

### Frontend no carga

```bash
# Verificar NGINX
sudo nginx -t
sudo systemctl status nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

---

## API Endpoints

### GET /api/status
Obtiene el estado del sistema

**Response:**
```json
{
  "listo": true,
  "documentos": 5,
  "chunks": 120,
  "gemini_habilitado": true
}
```

### POST /api/cargar
Carga documentos al sistema

**Request:**
```json
{
  "carpeta": "documentos",
  "tamano_chunk": 400
}
```

### POST /api/preguntar
Procesa una pregunta

**Request:**
```json
{
  "pregunta": "¿Qué es el emprendimiento?",
  "top_k": 3,
  "usar_gemini": true
}
```

**Response:**
```json
{
  "success": true,
  "respuesta": "El emprendimiento es...",
  "chunks": [...],
  "estadisticas": {...}
}
```

---

## Contribuciones

Para sugerencias o mejoras, abra un issue en el repositorio.

---

## Licencia

MIT License

---

## Autor

Proyecto desarrollado para análisis inteligente de documentos con IA.

---

## Soporte

Para problemas o preguntas:
- Abrir un issue en GitHub
- Revisar la documentación de AWS
- Consultar logs del sistema