"""
Base de Datos para Conversaciones - StudentBot
BD: SQLite (simple, no requiere servidor)
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import os

class DatabaseManager:
    """Gestor de base de datos para conversaciones y documentos"""
    
    def __init__(self, db_path="studentbot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de conversaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pregunta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                respuesta_mejorada TEXT,
                chunks_usados TEXT,
                relevancia_promedio REAL,
                gemini_usado BOOLEAN DEFAULT 0,
                tiempo_respuesta REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de documentos cargados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_archivo TEXT NOT NULL,
                ruta_original TEXT,
                ruta_s3 TEXT,
                tipo TEXT NOT NULL,
                tamano_bytes INTEGER,
                num_chunks INTEGER,
                metodo_extraccion TEXT,
                fecha_carga DATETIME DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1
            )
        """)
        
        # Tabla de sesiones (opcional, para múltiples usuarios)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sesion_id TEXT UNIQUE NOT NULL,
                fecha_inicio DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_ultima_actividad DATETIME DEFAULT CURRENT_TIMESTAMP,
                num_consultas INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✓ Base de datos inicializada: {self.db_path}")
    
    def guardar_conversacion(self, pregunta: str, respuesta: str, 
                            chunks: List[Dict], estadisticas: Dict,
                            respuesta_mejorada: str = None) -> int:
        """Guarda una conversación en la BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        chunks_json = json.dumps([{
            'fuente': c.get('fuente'),
            'relevancia': c.get('relevancia')
        } for c in chunks])
        
        cursor.execute("""
            INSERT INTO conversaciones 
            (pregunta, respuesta, respuesta_mejorada, chunks_usados, 
             relevancia_promedio, gemini_usado, tiempo_respuesta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pregunta,
            respuesta,
            respuesta_mejorada,
            chunks_json,
            estadisticas.get('relevancia_promedio', 0),
            estadisticas.get('gemini_usado', False),
            estadisticas.get('tiempo_respuesta', 0)
        ))
        
        conversacion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return conversacion_id
    
    def obtener_historial(self, limite: int = 50) -> List[Dict]:
        """Obtiene el historial de conversaciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pregunta, respuesta, respuesta_mejorada, 
                   relevancia_promedio, gemini_usado, timestamp
            FROM conversaciones
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limite,))
        
        conversaciones = []
        for row in cursor.fetchall():
            conversaciones.append({
                'id': row[0],
                'pregunta': row[1],
                'respuesta': row[2],
                'respuesta_mejorada': row[3],
                'relevancia': row[4],
                'gemini_usado': bool(row[5]),
                'timestamp': row[6]
            })
        
        conn.close()
        return conversaciones
    
    def buscar_conversaciones(self, termino: str, limite: int = 20) -> List[Dict]:
        """Busca conversaciones por término"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pregunta, respuesta, timestamp
            FROM conversaciones
            WHERE pregunta LIKE ? OR respuesta LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f'%{termino}%', f'%{termino}%', limite))
        
        resultados = []
        for row in cursor.fetchall():
            resultados.append({
                'id': row[0],
                'pregunta': row[1],
                'respuesta': row[2][:200] + '...',
                'timestamp': row[3]
            })
        
        conn.close()
        return resultados
    
    def registrar_documento(self, nombre: str, ruta: str, tipo: str, 
                           tamano: int, num_chunks: int, 
                           metodo: str = 'directo', ruta_s3: str = None) -> int:
        """Registra un documento cargado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documentos 
            (nombre_archivo, ruta_original, ruta_s3, tipo, 
             tamano_bytes, num_chunks, metodo_extraccion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, ruta, ruta_s3, tipo, tamano, num_chunks, metodo))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return doc_id
    
    def obtener_documentos_activos(self) -> List[Dict]:
        """Lista documentos activos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nombre_archivo, tipo, tamano_bytes, 
                   num_chunks, fecha_carga, ruta_s3
            FROM documentos
            WHERE activo = 1
            ORDER BY fecha_carga DESC
        """)
        
        documentos = []
        for row in cursor.fetchall():
            documentos.append({
                'id': row[0],
                'nombre': row[1],
                'tipo': row[2],
                'tamano': row[3],
                'chunks': row[4],
                'fecha': row[5],
                'en_s3': bool(row[6])
            })
        
        conn.close()
        return documentos
    
    def eliminar_documento(self, doc_id: int):
        """Marca documento como inactivo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE documentos 
            SET activo = 0 
            WHERE id = ?
        """, (doc_id,))
        
        conn.commit()
        conn.close()
    
    def obtener_estadisticas_generales(self) -> Dict:
        """Estadísticas generales del sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de conversaciones
        cursor.execute("SELECT COUNT(*) FROM conversaciones")
        total_conversaciones = cursor.fetchone()[0]
        
        # Conversaciones con Gemini
        cursor.execute("SELECT COUNT(*) FROM conversaciones WHERE gemini_usado = 1")
        con_gemini = cursor.fetchone()[0]
        
        # Documentos activos
        cursor.execute("SELECT COUNT(*) FROM documentos WHERE activo = 1")
        docs_activos = cursor.fetchone()[0]
        
        # Relevancia promedio
        cursor.execute("SELECT AVG(relevancia_promedio) FROM conversaciones")
        relevancia_avg = cursor.fetchone()[0] or 0
        
        # Tiempo promedio de respuesta
        cursor.execute("SELECT AVG(tiempo_respuesta) FROM conversaciones")
        tiempo_avg = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_conversaciones': total_conversaciones,
            'conversaciones_gemini': con_gemini,
            'documentos_activos': docs_activos,
            'relevancia_promedio': round(relevancia_avg, 3),
            'tiempo_promedio_respuesta': round(tiempo_avg, 2)
        }
    
    def limpiar_conversaciones_antiguas(self, dias: int = 30):
        """Elimina conversaciones más antiguas que X días"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM conversaciones 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """, (dias,))
        
        eliminadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        return eliminadas
    
    def exportar_conversaciones_json(self, archivo: str = "conversaciones_export.json"):
        """Exporta conversaciones a JSON"""
        conversaciones = self.obtener_historial(limite=1000)
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(conversaciones, f, ensure_ascii=False, indent=2)
        
        print(f"✓ {len(conversaciones)} conversaciones exportadas a {archivo}")
        return archivo


# Funciones auxiliares
def crear_backup(db_path="studentbot.db", backup_dir="backups"):
    """Crea backup de la base de datos"""
    import shutil
    from datetime import datetime
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"studentbot_backup_{timestamp}.db")
    
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup creado: {backup_path}")
    return backup_path


# Ejemplo de uso
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Guardar conversación de prueba
    db.guardar_conversacion(
        pregunta="¿Qué es el emprendimiento?",
        respuesta="El emprendimiento es el proceso de...",
        chunks=[{'fuente': 'test.pdf', 'relevancia': 0.85}],
        estadisticas={'relevancia_promedio': 0.85, 'tiempo_respuesta': 1.2}
    )
    
    # Obtener estadísticas
    stats = db.obtener_estadisticas_generales()
    print(f"Estadísticas: {stats}")