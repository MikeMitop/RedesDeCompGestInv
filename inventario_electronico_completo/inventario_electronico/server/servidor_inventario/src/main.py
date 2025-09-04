import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime

# Añadir la ruta de la base de datos al sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
sys.path.append(project_root)

from database.database_manager import DatabaseManager

# --- Configuración de la Aplicación ---
app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = 'inventario-electronico-2024-servidor'

# Configurar CORS para permitir conexiones desde cualquier origen
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/socket.io/*": {"origins": "*"}})

# Configurar Socket.IO con CORS
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- Configuración de la Base de Datos ---
db_path = os.path.join(project_root, 'database', 'inventario.db')
db_manager = DatabaseManager(db_path)

print("="*20)
print("Servidor de Inventario Electrónico")
print("Máquina 1 - Visualización de Inventario")
print(f"Base de datos inicializada correctamente: {db_path}")
print(f"Puerto: 5000")
print("="*20)

# --- Rutas de la Interfaz Web ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# --- Rutas de la API ---

@app.route("/api/status")
def get_status():
    return jsonify({"status": "Servidor disponible"})

@app.route("/api/productos", methods=["GET", "POST"])
def productos():
    if request.method == "POST":
        data = request.json
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        nombre = data.get("nombre")
        cantidad = data.get("cantidad")
        precio = data.get("precio")
        categoria = data.get("categoria")
        proveedor = data.get("proveedor")
        descripcion = data.get("descripcion")

        if not all([nombre, cantidad, precio]):
            return jsonify({"error": "Faltan campos obligatorios (nombre, cantidad, precio)"}), 400

        try:
            cantidad = int(cantidad)
            precio = float(precio)
        except (ValueError, TypeError):
            return jsonify({"error": "Cantidad y precio deben ser números válidos"}), 400

        try:
            db_manager.crear_producto(
                nombre,
                cantidad,
                precio,
                descripcion,
                categoria,
                proveedor,
            )
            # Notificar a los clientes sobre el nuevo producto
            socketio.emit("update", {"message": "Inventario actualizado"})
            return jsonify({"message": "Producto agregado exitosamente", "product": data}), 201
        except Exception as e:
            return jsonify({"error": f"Error al agregar producto: {str(e)}"}), 500

    else:  # GET request
        try:
            productos_data = db_manager.obtener_productos()
            return jsonify(productos_data)
        except Exception as e:
            return jsonify({"error": f"Error al obtener productos: {str(e)}"}), 500

@app.route("/api/estadisticas")
def get_stats():
    try:
        stats = db_manager.obtener_estadisticas()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Error al obtener estadísticas: {str(e)}"}), 500

# --- Eventos de Socket.IO ---

@socketio.on('connect')
def handle_connect():
    print(f'Cliente conectado: {request.sid}')
    # Enviar inventario inicial al cliente recién conectado
    emit_inventory_update()

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('solicitar_inventario')
def handle_solicitar_inventario():
    # Maneja solicitudes de actualización del inventario
    emit_inventory_update()

def emit_inventory_update():
    try:
        productos = db_manager.obtener_productos() # Cambiado de get_all_products a obtener_productos
        stats = db_manager.obtener_estadisticas()
        socketio.emit('inventario_actualizado', {
            'productos': productos,
            'estadisticas': stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"Error al emitir actualización de inventario: {e}")

# ==================== PUNTO DE ENTRADA ====================

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


