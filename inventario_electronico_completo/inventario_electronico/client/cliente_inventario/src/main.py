import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'inventario-electronico-2024-cliente'

# Configurar CORS para permitir conexiones desde cualquier origen
CORS(app, origins="*")

# Configurar Socket.IO con CORS
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuración del servidor de inventario (Máquina 1)
SERVIDOR_INVENTARIO_URL = 'http://localhost:5000'  # URL del servidor de inventario
SERVIDOR_INVENTARIO_SOCKET_URL = 'http://localhost:5000'  # URL para Socket.IO

# IPs permitidas para el cliente (Máquina 2)
IPS_PERMITIDAS_CLIENTE = ['192.168.1.2', '192.168.1.3', '127.0.0.1', 'localhost']

# ==================== RUTAS PRINCIPALES ====================

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    """Crear un nuevo producto y enviarlo al servidor"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nombre_producto', 'cantidad', 'precio']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Preparar datos del producto
        producto_data = {
            'nombre': data['nombre_producto'],
            'cantidad': int(data['cantidad']),
            'precio': float(data['precio']),
            'descripcion': data.get('descripcion', ''),
            'categoria': data.get('categoria', ''),
            'proveedor': data.get('proveedor', '')
        }
        
        # Enviar al servidor de inventario via API
        response = requests.post(
            f'{SERVIDOR_INVENTARIO_URL}/api/productos',
            json=producto_data,
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            
            # Notificar via Socket.IO al servidor
            socketio.emit('producto_creado', {
                'producto': producto_data,
                'nombre': producto_data['nombre'],
                'timestamp': datetime.now().isoformat()
            }, namespace='/', room=None)
            
            return jsonify({
                'success': True,
                'mensaje': f'Producto "{producto_data["nombre"]}" creado exitosamente',
                'producto': result.get('producto', producto_data)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error al comunicarse con el servidor de inventario'
            }), 500
            
    except requests.exceptions.RequestException as e:
        # Si falla la comunicación HTTP, intentar via Socket.IO
        try:
            socketio.emit('crear_producto', producto_data)
            return jsonify({
                'success': True,
                'mensaje': f'Producto "{producto_data["nombre"]}" enviado via Socket.IO',
                'producto': producto_data
            })
        except Exception as socket_error:
            return jsonify({
                'success': False,
                'error': f'Error de comunicación: {str(e)}'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    """Actualizar un producto existente"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['nombre_producto', 'cantidad', 'precio']
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                return jsonify({
                    'success': False,
                    'error': f'El campo {field} es requerido'
                }), 400
        
        # Preparar datos del producto
        producto_data = {
            'id_producto': id_producto,
            'nombre': data['nombre_producto'],
            'cantidad': int(data['cantidad']),
            'precio': float(data['precio']),
            'descripcion': data.get('descripcion', ''),
            'categoria': data.get('categoria', ''),
            'proveedor': data.get('proveedor', '')
        }
        
        # Enviar al servidor de inventario via API
        response = requests.put(
            f'{SERVIDOR_INVENTARIO_URL}/api/productos/{id_producto}',
            json=producto_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Notificar via Socket.IO al servidor
            socketio.emit('producto_actualizado', {
                'id_producto': id_producto,
                'producto': producto_data,
                'nombre': producto_data['nombre'],
                'timestamp': datetime.now().isoformat()
            }, namespace='/', room=None)
            
            return jsonify({
                'success': True,
                'mensaje': f'Producto ID {id_producto} actualizado exitosamente',
                'producto': result.get('producto', producto_data)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error al comunicarse con el servidor de inventario'
            }), 500
            
    except requests.exceptions.RequestException as e:
        # Si falla la comunicación HTTP, intentar via Socket.IO
        try:
            socketio.emit('modificar_producto', producto_data)
            return jsonify({
                'success': True,
                'mensaje': f'Actualización del producto ID {id_producto} enviada via Socket.IO',
                'producto': producto_data
            })
        except Exception as socket_error:
            return jsonify({
                'success': False,
                'error': f'Error de comunicación: {str(e)}'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/productos/servidor', methods=['GET'])
def obtener_productos_servidor():
    """Obtener productos del servidor de inventario"""
    try:
        response = requests.get(
            f'{SERVIDOR_INVENTARIO_URL}/api/productos',
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({
                'success': False,
                'error': 'Error al obtener productos del servidor'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Error de comunicación con el servidor: {str(e)}'
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint de estado del cliente"""
    try:
        ip_cliente = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        
        # Verificar conexión con el servidor
        servidor_disponible = False
        try:
            response = requests.get(f'{SERVIDOR_INVENTARIO_URL}/api/status', timeout=5)
            servidor_disponible = response.status_code == 200
        except:
            pass
        
        return jsonify({
            'status': 'Cliente de Inventario Operativo',
            'ip_cliente': ip_cliente,
            'timestamp': datetime.now().isoformat(),
            'servidor_inventario': {
                'url': SERVIDOR_INVENTARIO_URL,
                'disponible': servidor_disponible
            },
            'mensaje': 'Cliente listo para enviar datos al servidor'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# ==================== EVENTOS SOCKET.IO ====================

@socketio.on('connect')
def handle_connect():
    """Maneja nuevas conexiones Socket.IO"""
    print(f'Cliente conectado: {request.sid}')
    emit('cliente_conectado', {
        'mensaje': 'Conectado al cliente de inventario',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja desconexiones Socket.IO"""
    print(f'Cliente desconectado: {request.sid}')

@socketio.on('test_servidor')
def handle_test_servidor():
    """Probar conexión con el servidor de inventario"""
    try:
        response = requests.get(f'{SERVIDOR_INVENTARIO_URL}/api/status', timeout=5)
        if response.status_code == 200:
            emit('test_resultado', {
                'success': True,
                'mensaje': 'Conexión con servidor exitosa',
                'servidor_info': response.json()
            })
        else:
            emit('test_resultado', {
                'success': False,
                'mensaje': 'Servidor no responde correctamente'
            })
    except Exception as e:
        emit('test_resultado', {
            'success': False,
            'mensaje': f'Error de conexión: {str(e)}'
        })

# ==================== SERVIR ARCHIVOS ESTÁTICOS ====================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Sirve archivos estáticos y la aplicación frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# ==================== PUNTO DE ENTRADA ====================

if __name__ == '__main__':
    print("=== Cliente de Inventario Electrónico ===")
    print("Máquina 2 - Ingreso de Datos")
    print("Puerto: 5001")
    print("Servidor de inventario:", SERVIDOR_INVENTARIO_URL)
    print("IPs permitidas:", IPS_PERMITIDAS_CLIENTE)
    print("=========================================")
    
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
