
// Script NS3 generado automáticamente para Inventario Electrónico Network
// Generado el: 2025-09-03T22:22:43.002547

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

int main (int argc, char *argv[])
{
    // Configuración de logging
    LogComponentEnable ("UdpEchoClientApplication", LOG_LEVEL_INFO);
    LogComponentEnable ("UdpEchoServerApplication", LOG_LEVEL_INFO);
    
    // Crear nodos
    NodeContainer nodes;
    nodes.Create (3);
    
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
}
