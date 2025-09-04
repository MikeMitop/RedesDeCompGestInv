// JavaScript para el Switch de Inventario - Máquina 3

class SwitchManager {
    constructor() {
        this.switchData = null;
        this.updateInterval = null;
        this.init();
    }

    init() {
        console.log('Inicializando Switch Manager...');
        this.updateStartTime();
        this.loadSwitchStatus();
        this.startAutoUpdate();
        this.setupEventListeners();
    }

    updateStartTime() {
        const startTimeElement = document.getElementById('startTime');
        if (startTimeElement) {
            startTimeElement.textContent = new Date().toLocaleString('es-ES');
        }
    }

    async loadSwitchStatus() {
        try {
            const response = await fetch('/api/switch/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.switchData = await response.json();
            this.updateUI();
            this.logActivity('Estado del switch actualizado');
            
        } catch (error) {
            console.error('Error al cargar estado del switch:', error);
            this.logActivity(`Error: ${error.message}`, 'error');
            this.showOfflineState();
        }
    }

    updateUI() {
        if (!this.switchData) return;

        // Actualizar estadísticas principales
        this.updateStats();
        
        // Actualizar información del switch
        this.updateSwitchInfo();
        
        // Actualizar servidores
        this.updateServers();
        
        // Actualizar métricas de tráfico
        this.updateTrafficMetrics();
    }

    updateStats() {
        const stats = this.switchData.estadisticas;
        
        // Total de peticiones
        const totalRequestsEl = document.getElementById('totalRequests');
        if (totalRequestsEl) {
            totalRequestsEl.textContent = stats.total_requests || 0;
        }

        // Servidores activos
        const activeServersEl = document.getElementById('activeServers');
        if (activeServersEl && this.switchData.servidores) {
            const activeCount = this.switchData.servidores.filter(s => s.activo).length;
            activeServersEl.textContent = activeCount;
        }

        // Latencia promedio
        const avgLatencyEl = document.getElementById('avgLatency');
        if (avgLatencyEl && stats.total_requests > 0) {
            const avgLatency = Math.round(stats.total_latency / stats.total_requests);
            avgLatencyEl.textContent = `${avgLatency}ms`;
        }

        // Total de errores
        const totalErrorsEl = document.getElementById('totalErrors');
        if (totalErrorsEl) {
            totalErrorsEl.textContent = stats.errores || 0;
        }
    }

    updateSwitchInfo() {
        const switchInfo = this.switchData.switch;
        
        // Estado del switch
        const switchStatusEl = document.getElementById('switchStatus');
        if (switchStatusEl) {
            switchStatusEl.textContent = switchInfo.status || 'Estado desconocido';
        }

        // Uptime
        const switchUptimeEl = document.getElementById('switchUptime');
        if (switchUptimeEl) {
            switchUptimeEl.textContent = `Uptime: ${switchInfo.uptime_formatted || 'Calculando...'}`;
        }

        // Indicador de estado
        const switchIndicatorEl = document.getElementById('switchIndicator');
        if (switchIndicatorEl) {
            switchIndicatorEl.className = 'status-indicator active';
        }
    }

    updateServers() {
        const serversContainer = document.getElementById('serversContainer');
        if (!serversContainer || !this.switchData.servidores) return;

        serversContainer.innerHTML = '';

        this.switchData.servidores.forEach(servidor => {
            const serverCard = this.createServerCard(servidor);
            serversContainer.appendChild(serverCard);
        });
    }

    createServerCard(servidor) {
        const card = document.createElement('div');
        card.className = `server-card ${servidor.activo ? 'active' : 'inactive'}`;
        
        const lastCheck = servidor.ultimo_check ? 
            new Date(servidor.ultimo_check).toLocaleTimeString('es-ES') : 
            'Nunca';
        
        const latencia = servidor.latencia ? 
            `${Math.round(servidor.latencia)}ms` : 
            'N/A';

        card.innerHTML = `
            <div class="server-header">
                <div class="server-name">${servidor.name}</div>
                <div class="server-status ${servidor.activo ? 'active' : 'inactive'}">
                    ${servidor.activo ? 'Activo' : 'Inactivo'}
                </div>
            </div>
            <div class="server-info">
                <div><strong>URL:</strong> ${servidor.url}</div>
                <div><strong>Versión:</strong> ${servidor.version}</div>
                <div><strong>Peso:</strong> ${servidor.peso}%</div>
                <div><strong>Latencia:</strong> ${latencia}</div>
                <div><strong>Último check:</strong> ${lastCheck}</div>
                <div><strong>Error:</strong> ${servidor.error || 'Ninguno'}</div>
            </div>
            <div class="server-actions">
                <button class="btn btn-small ${servidor.activo ? 'btn-secondary' : 'btn-primary'}" 
                        onclick="switchManager.toggleServer('${servidor.id}')">
                    <i class="fas fa-power-off"></i>
                    ${servidor.activo ? 'Desactivar' : 'Activar'}
                </button>
            </div>
        `;

        return card;
    }

    async toggleServer(serverId) {
        try {
            const response = await fetch(`/api/switch/servidor/${serverId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.logActivity(result.mensaje);
            
            // Recargar estado después de cambio
            await this.loadSwitchStatus();
            
        } catch (error) {
            console.error('Error al cambiar estado del servidor:', error);
            this.logActivity(`Error al cambiar servidor: ${error.message}`, 'error');
        }
    }

    updateTrafficMetrics() {
        const stats = this.switchData.estadisticas;
        
        // Peticiones del último minuto (simulado)
        const lastMinuteRequestsEl = document.getElementById('lastMinuteRequests');
        if (lastMinuteRequestsEl) {
            // Simulamos las peticiones del último minuto
            const lastMinute = Math.floor(Math.random() * 20);
            lastMinuteRequestsEl.textContent = lastMinute;
        }

        // Promedio de peticiones (simulado)
        const avgRequestsEl = document.getElementById('avgRequests');
        if (avgRequestsEl) {
            const avgRequests = stats.total_requests > 0 ? 
                Math.round(stats.total_requests / 10) : 0;
            avgRequestsEl.textContent = avgRequests;
        }

        // Actualizar distribución por servidor
        this.updateServerDistribution();
    }

    updateServerDistribution() {
        const distributionEl = document.getElementById('serverDistribution');
        if (!distributionEl || !this.switchData.estadisticas.requests_por_servidor) return;

        const requests = this.switchData.estadisticas.requests_por_servidor;
        const total = Object.values(requests).reduce((sum, count) => sum + count, 0);

        if (total === 0) {
            distributionEl.innerHTML = '<p style="text-align: center; color: #718096;">Sin datos de distribución</p>';
            return;
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 0.5rem;">';
        
        Object.entries(requests).forEach(([serverId, count]) => {
            const percentage = Math.round((count / total) * 100);
            const servidor = this.switchData.servidores.find(s => s.id === serverId);
            const serverName = servidor ? servidor.name : serverId;
            
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f7fafc; border-radius: 5px;">
                    <span style="font-size: 0.9rem; color: #2d3748;">${serverName}</span>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="width: 60px; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                            <div style="width: ${percentage}%; height: 100%; background: #667eea;"></div>
                        </div>
                        <span style="font-size: 0.8rem; color: #4a5568; min-width: 35px;">${percentage}%</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        distributionEl.innerHTML = html;
    }

    showOfflineState() {
        // Mostrar estado offline cuando no se puede conectar
        const switchStatusEl = document.getElementById('switchStatus');
        if (switchStatusEl) {
            switchStatusEl.textContent = 'Switch desconectado';
        }

        const switchIndicatorEl = document.getElementById('switchIndicator');
        if (switchIndicatorEl) {
            switchIndicatorEl.className = 'status-indicator inactive';
        }

        const connectionStatusEl = document.getElementById('connectionStatus');
        if (connectionStatusEl) {
            connectionStatusEl.innerHTML = `
                <i class="fas fa-circle" style="color: #f56565;"></i>
                <span>Switch Desconectado</span>
            `;
        }
    }

    logActivity(message, type = 'info') {
        const activityLog = document.getElementById('activityLog');
        if (!activityLog) return;

        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        
        const timestamp = new Date().toLocaleString('es-ES');
        const icon = type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '✅';
        
        activityItem.innerHTML = `
            <span class="activity-time">${timestamp}</span>
            <span class="activity-text">${icon} ${message}</span>
        `;

        // Insertar al principio del log
        const firstChild = activityLog.firstChild;
        if (firstChild) {
            activityLog.insertBefore(activityItem, firstChild);
        } else {
            activityLog.appendChild(activityItem);
        }

        // Limitar a 50 entradas
        const items = activityLog.querySelectorAll('.activity-item');
        if (items.length > 50) {
            items[items.length - 1].remove();
        }
    }

    startAutoUpdate() {
        // Actualizar cada 5 segundos
        this.updateInterval = setInterval(() => {
            this.loadSwitchStatus();
        }, 5000);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    setupEventListeners() {
        // Manejar visibilidad de la página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoUpdate();
            } else {
                this.startAutoUpdate();
            }
        });

        // Manejar errores de red
        window.addEventListener('online', () => {
            this.logActivity('Conexión restaurada');
            this.loadSwitchStatus();
        });

        window.addEventListener('offline', () => {
            this.logActivity('Conexión perdida', 'error');
            this.showOfflineState();
        });
    }
}

// Funciones globales para los botones
function refreshServers() {
    if (window.switchManager) {
        window.switchManager.loadSwitchStatus();
        window.switchManager.logActivity('Servidores actualizados manualmente');
    }
}

function clearActivity() {
    const activityLog = document.getElementById('activityLog');
    if (activityLog) {
        activityLog.innerHTML = `
            <div class="activity-item">
                <span class="activity-time">${new Date().toLocaleString('es-ES')}</span>
                <span class="activity-text">📋 Registro limpiado</span>
            </div>
        `;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.switchManager = new SwitchManager();
});

// Manejar errores globales
window.addEventListener('error', (event) => {
    console.error('Error global:', event.error);
    if (window.switchManager) {
        window.switchManager.logActivity(`Error de aplicación: ${event.error.message}`, 'error');
    }
});

