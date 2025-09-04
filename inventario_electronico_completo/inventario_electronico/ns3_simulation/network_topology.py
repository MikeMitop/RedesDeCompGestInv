#!/usr/bin/env python3
"""
Definición de Topología de Red para Sistema de Inventario
Configura la topología de red simulada con 3 nodos conectados
"""

import json
from datetime import datetime

# Definición de la topología de red
NETWORK_TOPOLOGY = {
    "metadata": {
        "name": "Inventario Electrónico Network",
        "description": "Topología de red para sistema de inventario distribuido",
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "nodes_count": 3,
        "links_count": 3
    },
    
    "nodes": {
        "servidor_inventario": {
            "id": 1,
            "name": "Servidor de Inventario",
            "type": "server",
            "ip_address": "192.168.1.1",
            "subnet_mask": "255.255.255.0",
            "port": 5000,
            "mac_address": "00:1A:2B:3C:4D:01",
            "position": {"x": 100, "y": 200},
            "services": [
                "HTTP Server (Flask)",
                "SQLite Database",
                "Socket.IO Server",
                "REST API"
            ],
            "resources": {
                "cpu_cores": 4,
                "ram_mb": 4096,
                "storage_gb": 100,
                "network_bandwidth_mbps": 1000
            },
            "os": "Ubuntu 22.04",
            "applications": [
                "inventario_server.py",
                "database_manager.py"
            ]
        },
        
        "cliente_ingreso": {
            "id": 2,
            "name": "Cliente de Ingreso de Datos",
            "type": "client",
            "ip_address": "192.168.1.2",
            "subnet_mask": "255.255.255.0",
            "port": 5001,
            "mac_address": "00:1A:2B:3C:4D:02",
            "position": {"x": 300, "y": 100},
            "services": [
                "HTTP Client",
                "Socket.IO Client",
                "Web Interface",
                "Data Input Forms"
            ],
            "resources": {
                "cpu_cores": 2,
                "ram_mb": 2048,
                "storage_gb": 50,
                "network_bandwidth_mbps": 100
            },
            "os": "Ubuntu 22.04",
            "applications": [
                "cliente_inventario.py",
                "web_interface.html"
            ]
        },
        
        "switch_balanceador": {
            "id": 3,
            "name": "Switch/Balanceador de Carga",
            "type": "switch",
            "ip_address": "192.168.1.3",
            "subnet_mask": "255.255.255.0",
            "port": 5002,
            "mac_address": "00:1A:2B:3C:4D:03",
            "position": {"x": 200, "y": 300},
            "services": [
                "Load Balancer",
                "Reverse Proxy",
                "Health Monitor",
                "Traffic Router"
            ],
            "resources": {
                "cpu_cores": 8,
                "ram_mb": 8192,
                "storage_gb": 200,
                "network_bandwidth_mbps": 10000
            },
            "os": "Ubuntu 22.04",
            "applications": [
                "switch_inventario.py",
                "load_balancer.py"
            ]
        }
    },
    
    "links": {
        "cliente_to_switch": {
            "id": "link_1",
            "name": "Cliente -> Switch",
            "source": "cliente_ingreso",
            "target": "switch_balanceador",
            "type": "ethernet",
            "bandwidth_mbps": 100,
            "latency_ms": 5,
            "packet_loss_rate": 0.01,
            "duplex": "full",
            "protocol": "TCP/IP",
            "description": "Conexión del cliente al switch para envío de datos"
        },
        
        "switch_to_servidor": {
            "id": "link_2", 
            "name": "Switch -> Servidor",
            "source": "switch_balanceador",
            "target": "servidor_inventario",
            "type": "ethernet",
            "bandwidth_mbps": 1000,
            "latency_ms": 2,
            "packet_loss_rate": 0.005,
            "duplex": "full",
            "protocol": "TCP/IP",
            "description": "Conexión del switch al servidor de inventario"
        },
        
        "cliente_to_servidor": {
            "id": "link_3",
            "name": "Cliente -> Servidor (Directo)",
            "source": "cliente_ingreso", 
            "target": "servidor_inventario",
            "type": "ethernet",
            "bandwidth_mbps": 100,
            "latency_ms": 10,
            "packet_loss_rate": 0.02,
            "duplex": "full",
            "protocol": "TCP/IP",
            "description": "Conexión directa cliente-servidor (backup)"
        }
    },
    
    "traffic_patterns": {
        "product_creation": {
            "name": "Creación de Productos",
            "source": "cliente_ingreso",
            "destination": "servidor_inventario",
            "via": "switch_balanceador",
            "protocol": "HTTP POST",
            "frequency_per_minute": 10,
            "payload_size_bytes": 512,
            "priority": "high"
        },
        
        "inventory_query": {
            "name": "Consulta de Inventario",
            "source": "cliente_ingreso",
            "destination": "servidor_inventario", 
            "via": "switch_balanceador",
            "protocol": "HTTP GET",
            "frequency_per_minute": 5,
            "payload_size_bytes": 128,
            "priority": "medium"
        },
        
        "health_check": {
            "name": "Verificación de Salud",
            "source": "switch_balanceador",
            "destination": "servidor_inventario",
            "via": "direct",
            "protocol": "HTTP GET",
            "frequency_per_minute": 2,
            "payload_size_bytes": 64,
            "priority": "low"
        },
        
        "websocket_updates": {
            "name": "Actualizaciones en Tiempo Real",
            "source": "servidor_inventario",
            "destination": "cliente_ingreso",
            "via": "switch_balanceador",
            "protocol": "WebSocket",
            "frequency_per_minute": 20,
            "payload_size_bytes": 256,
            "priority": "medium"
        }
    },
    
    "network_parameters": {
        "subnet": "192.168.1.0/24",
        "gateway": "192.168.1.1",
        "dns_servers": ["8.8.8.8", "8.8.4.4"],
        "mtu": 1500,
        "simulation_duration_seconds": 300,
        "monitoring_interval_seconds": 10
    },
    
    "quality_of_service": {
        "high_priority": {
            "bandwidth_guarantee_percent": 60,
            "max_latency_ms": 50,
            "max_jitter_ms": 10
        },
        "medium_priority": {
            "bandwidth_guarantee_percent": 30,
            "max_latency_ms": 100,
            "max_jitter_ms": 20
        },
        "low_priority": {
            "bandwidth_guarantee_percent": 10,
            "max_latency_ms": 200,
            "max_jitter_ms": 50
        }
    }
}

def save_topology_to_file(filename="network_topology.json"):
    """Guarda la topología en un archivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(NETWORK_TOPOLOGY, f, indent=2, ensure_ascii=False)
    print(f"Topología guardada en {filename}")

def load_topology_from_file(filename="network_topology.json"):
    """Carga la topología desde un archivo JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Archivo {filename} no encontrado")
        return None

def print_topology_summary():
    """Imprime un resumen de la topología"""
    print("=== Resumen de Topología de Red ===")
    print(f"Nombre: {NETWORK_TOPOLOGY['metadata']['name']}")
    print(f"Nodos: {NETWORK_TOPOLOGY['metadata']['nodes_count']}")
    print(f"Enlaces: {NETWORK_TOPOLOGY['metadata']['links_count']}")
    
    print("\nNodos:")
    for node_id, node in NETWORK_TOPOLOGY['nodes'].items():
        print(f"  {node['name']} ({node['ip_address']}:{node['port']})")
        print(f"    Tipo: {node['type']}")
        print(f"    Servicios: {len(node['services'])}")
    
    print("\nEnlaces:")
    for link_id, link in NETWORK_TOPOLOGY['links'].items():
        print(f"  {link['name']}")
        print(f"    {link['source']} -> {link['target']}")
        print(f"    Ancho de banda: {link['bandwidth_mbps']} Mbps")
        print(f"    Latencia: {link['latency_ms']} ms")
    
    print("\nPatrones de Tráfico:")
    for pattern_id, pattern in NETWORK_TOPOLOGY['traffic_patterns'].items():
        print(f"  {pattern['name']}")
        print(f"    Frecuencia: {pattern['frequency_per_minute']}/min")
        print(f"    Tamaño: {pattern['payload_size_bytes']} bytes")

def validate_topology():
    """Valida la consistencia de la topología"""
    errors = []
    
    # Verificar que todos los nodos referenciados en enlaces existen
    node_ids = set(NETWORK_TOPOLOGY['nodes'].keys())
    
    for link_id, link in NETWORK_TOPOLOGY['links'].items():
        if link['source'] not in node_ids:
            errors.append(f"Enlace {link_id}: nodo origen '{link['source']}' no existe")
        if link['target'] not in node_ids:
            errors.append(f"Enlace {link_id}: nodo destino '{link['target']}' no existe")
    
    # Verificar patrones de tráfico
    for pattern_id, pattern in NETWORK_TOPOLOGY['traffic_patterns'].items():
        if pattern['source'] not in node_ids:
            errors.append(f"Patrón {pattern_id}: nodo origen '{pattern['source']}' no existe")
        if pattern['destination'] not in node_ids:
            errors.append(f"Patrón {pattern_id}: nodo destino '{pattern['destination']}' no existe")
    
    if errors:
        print("Errores de validación encontrados:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("Topología validada correctamente")
        return True

def generate_ns3_script():
    """Genera un script básico para NS3"""
    script_content = f"""
// Script NS3 generado automáticamente para {NETWORK_TOPOLOGY['metadata']['name']}
// Generado el: {datetime.now().isoformat()}

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

int main (int argc, char *argv[])
{{
    // Configuración de logging
    LogComponentEnable ("UdpEchoClientApplication", LOG_LEVEL_INFO);
    LogComponentEnable ("UdpEchoServerApplication", LOG_LEVEL_INFO);
    
    // Crear nodos
    NodeContainer nodes;
    nodes.Create ({NETWORK_TOPOLOGY['metadata']['nodes_count']});
    
    // Configurar enlaces point-to-point
    PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("100Mbps"));
    pointToPoint.SetChannelAttribute ("Delay", StringValue ("5ms"));
    
    // Instalar stack de Internet
    InternetStackHelper stack;
    stack.Install (nodes);
    
    // Configurar direcciones IP
    Ipv4AddressHelper address;
    address.SetBase ("192.168.1.0", "255.255.255.0");
    
    // Ejecutar simulación
    Simulator::Run ();
    Simulator::Destroy ();
    
    return 0;
}}
"""
    
    with open("inventario_ns3_simulation.cc", 'w') as f:
        f.write(script_content)
    
    print("Script NS3 generado: inventario_ns3_simulation.cc")

if __name__ == "__main__":
    print("Configurador de Topología de Red - Sistema de Inventario")
    
    # Validar topología
    if validate_topology():
        # Mostrar resumen
        print_topology_summary()
        
        # Guardar en archivo
        save_topology_to_file()
        
        # Generar script NS3
        generate_ns3_script()
        
        print("\nConfiguración de topología completada exitosamente")
    else:
        print("Error: La topología contiene errores y no puede ser utilizada")

