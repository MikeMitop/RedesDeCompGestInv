import os, sys, json, random, time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'inventario-electronico-2024-switch'
CORS(app)  # permite CORS

HEALTH_ENDPOINT = "/api/status"

# ======= SERVIDORES (NO uses el puerto del switch aquí) =======
SERVIDORES_INVENTARIO = [
    {
        'id': 'servidor_v1',
        'name': 'Servidor Principal v1.0',
        'url': 'http://127.0.0.1:5000',    # antes: localhost:5000
        'version': '1.0',
        'activo': True,
        'peso': 70
    },
    {
        'id': 'servidor_v2',
        'name': 'Servidor Backup v1.1',
        'url': 'http://127.0.0.1:5003',    # antes: 5002 (colisionaba con el switch)
        'version': '1.1',
        'activo': False,
        'peso': 30
    }
]
# Derivar health_check_url
for s in SERVIDORES_INVENTARIO:
    s['health_check_url'] = s['url'] + HEALTH_ENDPOINT

CLIENTES_PERMITIDOS = [
    {'id': 'cliente_v1', 'name': 'Cliente Principal v1.0', 'url': 'http://127.0.0.1:5001', 'version': '1.0', 'activo': True}
]

estadisticas_switch = {
    'total_requests': 0,
    'requests_por_servidor': {},
    'errores': 0,
    'uptime_inicio': datetime.now(),
    'health_checks': 0
}

IPS_PERMITIDAS_SWITCH = ['127.0.0.1', 'localhost', '192.168.1.4', '10.0.0.3']

# ==================== UTILIDAD ====================
def obtener_servidor_disponible():
    activos = [s for s in SERVIDORES_INVENTARIO if s['activo']]
    if not activos:
        return None
    total_peso = sum(s['peso'] for s in activos)
    r = random.randint(1, total_peso)
    acc = 0
    for s in activos:
        acc += s['peso']
        if r <= acc:
            return s
    return activos[0]

def verificar_salud_servidores():
    for s in SERVIDORES_INVENTARIO:
        try:
            r = requests.get(s['health_check_url'], timeout=5)
            s['activo'] = (r.status_code == 200)
            s['ultimo_check'] = datetime.now()
            s['latencia'] = r.elapsed.total_seconds() * 1000
            s.pop('error', None)
        except Exception as e:
            s['activo'] = False
            s['ultimo_check'] = datetime.now()
            s['error'] = str(e)
    estadisticas_switch['health_checks'] += 1

def proxy_request(target_url, method='GET', data=None, headers=None):
    try:
        excluded = {'host', 'content-length', 'connection'}
        proxy_headers = {k: v for k, v in (headers or {}).items() if k.lower() not in excluded}

        if method == 'GET':
            r = requests.get(target_url, headers=proxy_headers, timeout=30)
        elif method == 'POST':
            r = requests.post(target_url, json=data, headers=proxy_headers, timeout=30)
        elif method == 'PUT':
            r = requests.put(target_url, json=data, headers=proxy_headers, timeout=30)
        elif method == 'DELETE':
            r = requests.delete(target_url, headers=proxy_headers, timeout=30)
        else:
            return None, f"Método HTTP no soportado: {method}"
        return r, None
    except requests.exceptions.Timeout:
        return None, "Timeout en la petición al servidor"
    except requests.exceptions.ConnectionError:
        return None, "Error de conexión con el servidor"
    except Exception as e:
        return None, f"Error en proxy: {e}"

# ==================== RUTAS SWITCH ====================
@app.get('/api/switch/status')
def switch_status():
    verificar_salud_servidores()
    uptime = datetime.now() - estadisticas_switch['uptime_inicio']
    return jsonify({
        'switch': {'status': 'Switch de Inventario Operativo', 'version': '1.0',
                   'uptime_seconds': uptime.total_seconds(), 'uptime_formatted': str(uptime).split('.')[0]},
        'servidores': SERVIDORES_INVENTARIO,
        'clientes': CLIENTES_PERMITIDOS,
        'estadisticas': estadisticas_switch,
        'timestamp': datetime.now().isoformat()
    })

@app.get('/api/switch/servidores')
def listar_servidores():
    verificar_salud_servidores()
    return jsonify({
        'success': True,
        'servidores': SERVIDORES_INVENTARIO,
        'total': len(SERVIDORES_INVENTARIO),
        'activos': len([s for s in SERVIDORES_INVENTARIO if s['activo']])
    })

@app.post('/api/switch/servidor/<servidor_id>/toggle')
def toggle_servidor(servidor_id):
    s = next((x for x in SERVIDORES_INVENTARIO if x['id'] == servidor_id), None)
    if not s:
        return jsonify({'success': False, 'error': f'Servidor {servidor_id} no encontrado'}), 404
    s['activo'] = not s['activo']
    return jsonify({'success': True, 'mensaje': f'Servidor {servidor_id} {"activado" if s["activo"] else "desactivado"}', 'servidor': s})

# ==================== PROXY ====================
@app.route('/api/productos', methods=['GET', 'POST'])
def proxy_productos():
    s = obtener_servidor_disponible()
    if not s:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': 'No hay servidores disponibles'}), 503

    data = request.get_json() if request.method == 'POST' else None
    r, err = proxy_request(f"{s['url']}/api/productos", method=request.method, data=data, headers=dict(request.headers))

    estadisticas_switch['total_requests'] += 1
    estadisticas_switch['requests_por_servidor'][s['id']] = estadisticas_switch['requests_por_servidor'].get(s['id'], 0) + 1

    if err:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': err, 'servidor_intentado': s['name']}), 502

    body = r.json() if r.content else {}
    if isinstance(body, dict):
        body['_switch_info'] = {'servidor_usado': s['name'], 'servidor_version': s['version'], 'timestamp': datetime.now().isoformat()}
    return Response(json.dumps(body), status=r.status_code, mimetype='application/json')

@app.route('/api/productos/<int:producto_id>', methods=['GET', 'PUT', 'DELETE'])
def proxy_producto_especifico(producto_id):
    s = obtener_servidor_disponible()
    if not s:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': 'No hay servidores disponibles'}), 503

    data = request.get_json() if request.method in ['PUT', 'POST'] else None
    r, err = proxy_request(f"{s['url']}/api/productos/{producto_id}", method=request.method, data=data, headers=dict(request.headers))

    estadisticas_switch['total_requests'] += 1
    estadisticas_switch['requests_por_servidor'][s['id']] = estadisticas_switch['requests_por_servidor'].get(s['id'], 0) + 1

    if err:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': err, 'servidor_intentado': s['name']}), 502

    body = r.json() if r.content else {}
    if isinstance(body, dict):
        body['_switch_info'] = {'servidor_usado': s['name'], 'servidor_version': s['version'], 'timestamp': datetime.now().isoformat()}
    return Response(json.dumps(body), status=r.status_code, mimetype='application/json')

@app.get('/api/clientes')
def proxy_clientes():
    s = obtener_servidor_disponible()
    if not s:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': 'No hay servidores disponibles'}), 503

    r, err = proxy_request(f"{s['url']}/api/clientes", method='GET', headers=dict(request.headers))

    estadisticas_switch['total_requests'] += 1
    estadisticas_switch['requests_por_servidor'][s['id']] = estadisticas_switch['requests_por_servidor'].get(s['id'], 0) + 1

    if err:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': err, 'servidor_intentado': s['name']}), 502

    body = r.json() if r.content else {}
    if isinstance(body, dict):
        body['_switch_info'] = {'servidor_usado': s['name'], 'servidor_version': s['version'], 'timestamp': datetime.now().isoformat()}
    return Response(json.dumps(body), status=r.status_code, mimetype='application/json')

@app.get('/api/estadisticas')
def proxy_estadisticas():
    s = obtener_servidor_disponible()
    if not s:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': 'No hay servidores disponibles'}), 503

    r, err = proxy_request(f"{s['url']}/api/estadisticas", method='GET', headers=dict(request.headers))

    estadisticas_switch['total_requests'] += 1
    estadisticas_switch['requests_por_servidor'][s['id']] = estadisticas_switch['requests_por_servidor'].get(s['id'], 0) + 1

    if err:
        estadisticas_switch['errores'] += 1
        return jsonify({'success': False, 'error': err, 'servidor_intentado': s['name']}), 502

    body = r.json() if r.content else {}
    if isinstance(body, dict):
        body['_switch_info'] = {'servidor_usado': s['name'], 'servidor_version': s['version'], 'timestamp': datetime.now().isoformat()}
    return Response(json.dumps(body), status=r.status_code, mimetype='application/json')

# Health check periódico
@app.before_request
def _check_periodico():
    if estadisticas_switch['total_requests'] % 10 == 0:
        verificar_salud_servidores()

# Static / frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if not static_folder_path:
        return "Static folder not configured", 404
    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    index_path = os.path.join(static_folder_path, 'index.html')
    return send_from_directory(static_folder_path, 'index.html') if os.path.exists(index_path) else ("index.html not found", 404)

if __name__ == '__main__':
    print("=== Switch de Inventario Electrónico ===")
    print("Máquina 3 - Switch/Balanceador de Carga")
    print("Puerto: 5002")
    for s in SERVIDORES_INVENTARIO:
        print(f"  - {s['name']} ({s['url']}) - Peso: {s['peso']}%")
    print("IPs permitidas:", IPS_PERMITIDAS_SWITCH)
    verificar_salud_servidores()
    app.run(host='0.0.0.0', port=5002, debug=True)

