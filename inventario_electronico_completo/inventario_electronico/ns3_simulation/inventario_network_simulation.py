#!/usr/bin/env python3
"""
Simulación de Red para Sistema de Inventario Electrónico
Simula la comunicación entre 3 máquinas:
- Máquina 1: Servidor de Inventario (Puerto 5000)
- Máquina 2: Cliente de Ingreso de Datos (Puerto 5001)  
- Máquina 3: Switch/Balanceador de Carga (Puerto 5002)

Autor: Sistema de Inventario Electrónico
Fecha: 2024
"""

import socket
import threading
import time
import json
import random
from datetime import datetime
import sys
import os

# Configuración de la simulación
SIMULATION_CONFIG = {
    'duration': 60,  # Duración en segundos
    'packet_loss_rate': 0.02,  # 2% de pérdida de paquetes
    'latency_min': 10,  # Latencia mínima en ms
    'latency_max': 50,  # Latencia máxima en ms
    'bandwidth_limit': 1000,  # Límite de ancho de banda en KB/s
}

# Configuración de nodos
NODES = {
    'servidor': {
        'id': 1,
        'name': 'Servidor de Inventario',
        'ip': '192.168.1.1',
        'port': 5000,
        'type': 'server',
        'services': ['inventory_api', 'database', 'websocket']
    },
    'cliente': {
        'id': 2,
        'name': 'Cliente de Ingreso',
        'ip': '192.168.1.2',
        'port': 5001,
        'type': 'client',
        'services': ['data_input', 'websocket_client']
    },
    'switch': {
        'id': 3,
        'name': 'Switch/Balanceador',
        'ip': '192.168.1.3',
        'port': 5002,
        'type': 'switch',
        'services': ['load_balancer', 'proxy', 'health_check']
    }
}

# Estadísticas de la simulación
simulation_stats = {
    'packets_sent': 0,
    'packets_received': 0,
    'packets_lost': 0,
    'total_latency': 0,
    'connections': 0,
    'errors': 0,
    'start_time': None,
    'node_stats': {}
}

class NetworkNode:
    """Representa un nodo en la red simulada"""
    
    def __init__(self, node_id, config):
        self.id = node_id
        self.config = config
        self.name = config['name']
        self.ip = config['ip']
        self.port = config['port']
        self.type = config['type']
        self.services = config['services']
        self.is_active = True
        self.connections = []
        self.message_queue = []
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'uptime': 0,
            'errors': 0
        }
        
    def send_message(self, target_node, message_type, data):
        """Envía un mensaje a otro nodo"""
        if not self.is_active:
            return False
            
        # Simular latencia de red
        latency = random.randint(SIMULATION_CONFIG['latency_min'], 
                               SIMULATION_CONFIG['latency_max'])
        
        # Simular pérdida de paquetes
        if random.random() < SIMULATION_CONFIG['packet_loss_rate']:
            simulation_stats['packets_lost'] += 1
            self.stats['errors'] += 1
            return False
        
        message = {
            'from': self.id,
            'to': target_node.id,
            'type': message_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'latency': latency
        }
        
        # Simular envío con latencia
        def delayed_send():
            time.sleep(latency / 1000.0)  # Convertir ms a segundos
            target_node.receive_message(message)
            
        threading.Thread(target=delayed_send, daemon=True).start()
        
        # Actualizar estadísticas
        self.stats['messages_sent'] += 1
        self.stats['bytes_sent'] += len(json.dumps(message))
        simulation_stats['packets_sent'] += 1
        simulation_stats['total_latency'] += latency
        
        return True
    
    def receive_message(self, message):
        """Recibe un mensaje de otro nodo"""
        if not self.is_active:
            return
            
        self.message_queue.append(message)
        self.stats['messages_received'] += 1
        self.stats['bytes_received'] += len(json.dumps(message))
        simulation_stats['packets_received'] += 1
        
        # Procesar mensaje según el tipo de nodo
        self.process_message(message)
    
    def process_message(self, message):
        """Procesa un mensaje recibido según el tipo de nodo"""
        msg_type = message['type']
        
        if self.type == 'server':
            self._process_server_message(message)
        elif self.type == 'client':
            self._process_client_message(message)
        elif self.type == 'switch':
            self._process_switch_message(message)
    
    def _process_server_message(self, message):
        """Procesa mensajes del servidor"""
        msg_type = message['type']
        
        if msg_type == 'product_create':
            # Simular creación de producto
            print(f"[{self.name}] Creando producto: {message['data']['nombre']}")
            
        elif msg_type == 'product_list':
            # Simular listado de productos
            print(f"[{self.name}] Enviando lista de productos")
            
        elif msg_type == 'health_check':
            # Responder health check
            print(f"[{self.name}] Health check recibido")
    
    def _process_client_message(self, message):
        """Procesa mensajes del cliente"""
        msg_type = message['type']
        
        if msg_type == 'product_response':
            print(f"[{self.name}] Producto procesado correctamente")
            
        elif msg_type == 'server_status':
            print(f"[{self.name}] Estado del servidor recibido")
    
    def _process_switch_message(self, message):
        """Procesa mensajes del switch"""
        msg_type = message['type']
        
        if msg_type == 'route_request':
            # Simular enrutamiento
            print(f"[{self.name}] Enrutando petición a servidor")
            
        elif msg_type == 'load_balance':
            print(f"[{self.name}] Balanceando carga entre servidores")

class NetworkSimulation:
    """Simulador de red principal"""
    
    def __init__(self):
        self.nodes = {}
        self.running = False
        self.start_time = None
        
        # Crear nodos
        for node_id, config in NODES.items():
            self.nodes[node_id] = NetworkNode(node_id, config)
            simulation_stats['node_stats'][node_id] = self.nodes[node_id].stats
    
    def start_simulation(self):
        """Inicia la simulación"""
        print("=== Iniciando Simulación de Red del Sistema de Inventario ===")
        print(f"Duración: {SIMULATION_CONFIG['duration']} segundos")
        print(f"Pérdida de paquetes: {SIMULATION_CONFIG['packet_loss_rate']*100}%")
        print(f"Latencia: {SIMULATION_CONFIG['latency_min']}-{SIMULATION_CONFIG['latency_max']} ms")
        print("=" * 60)
        
        self.running = True
        self.start_time = datetime.now()
        simulation_stats['start_time'] = self.start_time
        
        # Iniciar hilos de simulación
        threads = [
            threading.Thread(target=self._simulate_client_activity, daemon=True),
            threading.Thread(target=self._simulate_server_activity, daemon=True),
            threading.Thread(target=self._simulate_switch_activity, daemon=True),
            threading.Thread(target=self._monitor_network, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        # Ejecutar simulación por el tiempo especificado
        time.sleep(SIMULATION_CONFIG['duration'])
        
        self.stop_simulation()
    
    def _simulate_client_activity(self):
        """Simula actividad del cliente"""
        cliente = self.nodes['cliente']
        servidor = self.nodes['servidor']
        switch = self.nodes['switch']
        
        while self.running:
            # Simular creación de productos
            if random.random() < 0.3:  # 30% probabilidad cada ciclo
                producto_data = {
                    'nombre': f'Producto_{random.randint(1000, 9999)}',
                    'cantidad': random.randint(1, 100),
                    'precio': round(random.uniform(10.0, 1000.0), 2),
                    'categoria': random.choice(['Electrónicos', 'Computadoras', 'Accesorios'])
                }
                
                # Enviar a través del switch
                cliente.send_message(switch, 'product_create', producto_data)
            
            # Simular consulta de productos
            if random.random() < 0.2:  # 20% probabilidad
                cliente.send_message(switch, 'product_list', {})
            
            time.sleep(random.uniform(2, 5))  # Esperar entre 2-5 segundos
    
    def _simulate_server_activity(self):
        """Simula actividad del servidor"""
        servidor = self.nodes['servidor']
        cliente = self.nodes['cliente']
        
        while self.running:
            # Procesar mensajes en cola
            if servidor.message_queue:
                message = servidor.message_queue.pop(0)
                
                # Simular procesamiento
                time.sleep(random.uniform(0.1, 0.5))
                
                # Responder al cliente
                if message['type'] == 'product_create':
                    response_data = {
                        'success': True,
                        'product_id': random.randint(1, 1000),
                        'message': 'Producto creado exitosamente'
                    }
                    servidor.send_message(cliente, 'product_response', response_data)
            
            time.sleep(0.5)
    
    def _simulate_switch_activity(self):
        """Simula actividad del switch"""
        switch = self.nodes['switch']
        servidor = self.nodes['servidor']
        
        while self.running:
            # Procesar mensajes en cola del switch
            if switch.message_queue:
                message = switch.message_queue.pop(0)
                
                # Reenviar al servidor apropiado
                if message['type'] in ['product_create', 'product_list']:
                    switch.send_message(servidor, message['type'], message['data'])
            
            # Simular health checks
            if random.random() < 0.1:  # 10% probabilidad
                switch.send_message(servidor, 'health_check', {})
            
            time.sleep(1)
    
    def _monitor_network(self):
        """Monitorea el estado de la red"""
        while self.running:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            print(f"\n[{elapsed:.1f}s] Estado de la Red:")
            print(f"  Paquetes enviados: {simulation_stats['packets_sent']}")
            print(f"  Paquetes recibidos: {simulation_stats['packets_received']}")
            print(f"  Paquetes perdidos: {simulation_stats['packets_lost']}")
            
            if simulation_stats['packets_received'] > 0:
                avg_latency = simulation_stats['total_latency'] / simulation_stats['packets_received']
                print(f"  Latencia promedio: {avg_latency:.1f} ms")
            
            # Estado de nodos
            for node_id, node in self.nodes.items():
                print(f"  {node.name}: {node.stats['messages_sent']} enviados, "
                      f"{node.stats['messages_received']} recibidos")
            
            time.sleep(10)  # Actualizar cada 10 segundos
    
    def stop_simulation(self):
        """Detiene la simulación"""
        self.running = False
        print("\n" + "=" * 60)
        print("=== Simulación Completada ===")
        self._print_final_stats()
    
    def _print_final_stats(self):
        """Imprime estadísticas finales"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\nDuración total: {elapsed:.1f} segundos")
        print(f"Paquetes totales enviados: {simulation_stats['packets_sent']}")
        print(f"Paquetes totales recibidos: {simulation_stats['packets_received']}")
        print(f"Paquetes perdidos: {simulation_stats['packets_lost']}")
        
        if simulation_stats['packets_sent'] > 0:
            loss_rate = (simulation_stats['packets_lost'] / simulation_stats['packets_sent']) * 100
            print(f"Tasa de pérdida real: {loss_rate:.2f}%")
        
        if simulation_stats['packets_received'] > 0:
            avg_latency = simulation_stats['total_latency'] / simulation_stats['packets_received']
            print(f"Latencia promedio: {avg_latency:.1f} ms")
        
        print("\nEstadísticas por nodo:")
        for node_id, node in self.nodes.items():
            stats = node.stats
            print(f"\n{node.name} ({node.ip}:{node.port}):")
            print(f"  Mensajes enviados: {stats['messages_sent']}")
            print(f"  Mensajes recibidos: {stats['messages_received']}")
            print(f"  Bytes enviados: {stats['bytes_sent']}")
            print(f"  Bytes recibidos: {stats['bytes_received']}")
            print(f"  Errores: {stats['errors']}")
            print(f"  Servicios: {', '.join(node.services)}")

def main():
    """Función principal"""
    print("Sistema de Simulación de Red - Inventario Electrónico")
    print("Simulando topología de 3 máquinas con comunicación TCP/IP")
    
    try:
        # Crear y ejecutar simulación
        simulation = NetworkSimulation()
        simulation.start_simulation()
        
    except KeyboardInterrupt:
        print("\nSimulación interrumpida por el usuario")
    except Exception as e:
        print(f"Error en la simulación: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

