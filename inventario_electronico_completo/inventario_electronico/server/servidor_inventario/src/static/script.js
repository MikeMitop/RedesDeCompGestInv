// JavaScript para el Servidor de Inventario - Máquina 1

// Variables globales
let socket;
let productos = [];
let estadisticas = {};
let activityLog = [];

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Inicializar la aplicación
function initializeApp() {
    console.log('Inicializando Servidor de Inventario...');
    
    // Conectar Socket.IO
    connectSocket();
    
    // Cargar datos iniciales
    cargarDatosIniciales();
    
    // Configurar eventos
    setupEventListeners();
    
    // Mostrar loading inicial
    showLoading();
}

// Conectar Socket.IO
function connectSocket() {
    // Conectar al servidor Socket.IO
    socket = io();
    
    // Eventos de conexión
    socket.on('connect', function() {
        console.log('Conectado al servidor Socket.IO');
        updateConnectionStatus('connected', 'Conectado');
        hideLoading();
        showToast('Conectado al servidor', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Desconectado del servidor Socket.IO');
        updateConnectionStatus('disconnected', 'Desconectado');
        showToast('Conexión perdida', 'error');
    });
    
    socket.on('connect_error', function(error) {
        console.error('Error de conexión:', error);
        updateConnectionStatus('disconnected', 'Error de conexión');
        showToast('Error de conexión', 'error');
    });
    
    // Eventos de datos
    socket.on('inventario_inicial', function(data) {
        console.log('Inventario inicial recibido:', data);
        productos = data.productos || [];
        estadisticas = data.estadisticas || {};
        actualizarInterfaz();
        addActivityLog('Sistema iniciado', 'create');
    });
    
    socket.on('inventario_actualizado', function(data) {
        console.log('Inventario actualizado:', data);
        productos = data.productos || [];
        estadisticas = data.estadisticas || {};
        actualizarInterfaz();
        
        if (data.mensaje) {
            showToast(data.mensaje, 'success');
            addActivityLog(data.mensaje, data.accion || 'update');
        }
    });
    
    socket.on('actualizar_inventario', function(data) {
        console.log('Actualización de inventario recibida:', data);
        productos = data.productos || [];
        estadisticas = data.estadisticas || {};
        actualizarInterfaz();
    });
    
    socket.on('error', function(data) {
        console.error('Error del servidor:', data);
        showToast(data.mensaje || 'Error del servidor', 'error');
        addActivityLog('Error: ' + (data.mensaje || 'Error desconocido'), 'error');
    });
}

// Cargar datos iniciales via API REST
async function cargarDatosIniciales() {
    try {
        // Cargar productos
        const productosResponse = await fetch('/api/productos');
        if (productosResponse.ok) {
            const productosData = await productosResponse.json();
            if (productosData.success) {
                productos = productosData.productos;
            }
        }
        
        // Cargar estadísticas
        const statsResponse = await fetch('/api/estadisticas');
        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            if (statsData.success) {
                estadisticas = statsData.estadisticas;
            }
        }
        
        // Actualizar interfaz
        actualizarInterfaz();
        
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        showToast('Error cargando datos iniciales', 'error');
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Búsqueda en tiempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filtrarProductos);
    }
}

// Actualizar estado de conexión
function updateConnectionStatus(status, text) {
    const statusElement = document.getElementById('connectionStatus');
    const statusText = document.getElementById('statusText');
    
    if (statusElement && statusText) {
        statusElement.className = `status-indicator ${status}`;
        statusText.textContent = text;
    }
}

// Actualizar toda la interfaz
function actualizarInterfaz() {
    actualizarEstadisticas();
    actualizarTablaInventario();
    actualizarUltimaActualizacion();
}

// Actualizar estadísticas del dashboard
function actualizarEstadisticas() {
    const totalProductosEl = document.getElementById('totalProductos');
    const totalClientesEl = document.getElementById('totalClientes');
    const valorInventarioEl = document.getElementById('valorInventario');
    const stockBajoEl = document.getElementById('stockBajo');
    
    if (totalProductosEl) {
        totalProductosEl.textContent = estadisticas.total_productos || productos.length || 0;
    }
    
    if (totalClientesEl) {
        totalClientesEl.textContent = estadisticas.total_clientes || 0;
    }
    
    if (valorInventarioEl) {
        const valor = estadisticas.valor_inventario || 0;
        valorInventarioEl.textContent = `$${formatNumber(valor)}`;
    }
    
    if (stockBajoEl) {
        stockBajoEl.textContent = estadisticas.productos_stock_bajo || 0;
    }
}

// Actualizar tabla de inventario
function actualizarTablaInventario() {
    const tbody = document.getElementById('inventoryBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (!productos || productos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    <i class="fas fa-box-open" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
                    No hay productos en el inventario
                </td>
            </tr>
        `;
        return;
    }
    
    productos.forEach(producto => {
        const row = document.createElement('tr');
        
        // Determinar estado del stock
        let estadoStock = 'normal';
        let estadoTexto = 'Normal';
        
        if (producto.cantidad === 0) {
            estadoStock = 'out';
            estadoTexto = 'Agotado';
        } else if (producto.cantidad < 10) {
            estadoStock = 'low';
            estadoTexto = 'Stock Bajo';
        }
        
        const total = (producto.cantidad * producto.precio).toFixed(2);
        
        row.innerHTML = `
            <td><strong>#${producto.id_producto}</strong></td>
            <td>
                <div style="font-weight: 600;">${escapeHtml(producto.nombre_producto)}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">
                    ${producto.proveedor ? escapeHtml(producto.proveedor) : 'Sin proveedor'}
                </div>
            </td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">
                ${escapeHtml(producto.descripcion || 'Sin descripción')}
            </td>
            <td>
                <span style="background: var(--background-color); padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">
                    ${escapeHtml(producto.categoria || 'Sin categoría')}
                </span>
            </td>
            <td><strong>${producto.cantidad}</strong></td>
            <td>$${formatNumber(producto.precio)}</td>
            <td><strong>$${formatNumber(total)}</strong></td>
            <td>
                <span class="status-badge status-${estadoStock}">
                    ${estadoTexto}
                </span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Filtrar productos en la tabla
function filtrarProductos() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#inventoryBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        row.style.display = shouldShow ? '' : 'none';
    });
}

// Actualizar inventario manualmente
function actualizarInventario() {
    showLoading();
    
    if (socket && socket.connected) {
        socket.emit('solicitar_inventario');
        addActivityLog('Inventario actualizado manualmente', 'update');
    } else {
        // Fallback a API REST
        cargarDatosIniciales().then(() => {
            hideLoading();
            showToast('Inventario actualizado', 'success');
            addActivityLog('Inventario actualizado via API', 'update');
        });
    }
    
    setTimeout(hideLoading, 1000);
}

// Exportar datos (simulado)
function exportarDatos() {
    try {
        const data = {
            productos: productos,
            estadisticas: estadisticas,
            fecha_exportacion: new Date().toISOString(),
            total_productos: productos.length
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `inventario_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showToast('Datos exportados correctamente', 'success');
        addActivityLog('Datos exportados a JSON', 'export');
        
    } catch (error) {
        console.error('Error exportando datos:', error);
        showToast('Error al exportar datos', 'error');
    }
}

// Actualizar timestamp de última actualización
function actualizarUltimaActualizacion() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) {
        const now = new Date();
        lastUpdateEl.textContent = now.toLocaleString('es-ES');
    }
}

// Agregar entrada al log de actividad
function addActivityLog(message, type = 'info') {
    const logEntry = {
        message: message,
        type: type,
        timestamp: new Date()
    };
    
    activityLog.unshift(logEntry);
    
    // Mantener solo los últimos 50 logs
    if (activityLog.length > 50) {
        activityLog = activityLog.slice(0, 50);
    }
    
    updateActivityLogDisplay();
}

// Actualizar display del log de actividad
function updateActivityLogDisplay() {
    const logContainer = document.getElementById('activityLog');
    if (!logContainer) return;
    
    logContainer.innerHTML = '';
    
    if (activityLog.length === 0) {
        logContainer.innerHTML = `
            <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                <i class="fas fa-history" style="font-size: 1.5rem; margin-bottom: 10px; display: block;"></i>
                No hay actividad registrada
            </div>
        `;
        return;
    }
    
    activityLog.forEach(entry => {
        const item = document.createElement('div');
        item.className = `activity-item activity-${entry.type}`;
        
        let icon = 'fas fa-info-circle';
        if (entry.type === 'create') icon = 'fas fa-plus';
        else if (entry.type === 'update') icon = 'fas fa-edit';
        else if (entry.type === 'delete') icon = 'fas fa-trash';
        else if (entry.type === 'error') icon = 'fas fa-exclamation-triangle';
        else if (entry.type === 'export') icon = 'fas fa-download';
        
        item.innerHTML = `
            <div class="activity-icon">
                <i class="${icon}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-message">${escapeHtml(entry.message)}</div>
                <div class="activity-time">${entry.timestamp.toLocaleString('es-ES')}</div>
            </div>
        `;
        
        logContainer.appendChild(item);
    });
}

// Limpiar log de actividad
function limpiarLog() {
    activityLog = [];
    updateActivityLogDisplay();
    showToast('Log de actividad limpiado', 'success');
}

// Mostrar loading overlay
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('show');
    }
}

// Ocultar loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('show');
    }
}

// Mostrar toast notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');
    const toastIcon = toast.querySelector('.toast-icon');
    
    if (!toast || !toastMessage || !toastIcon) return;
    
    // Configurar icono según el tipo
    let iconClass = 'fas fa-info-circle';
    if (type === 'success') iconClass = 'fas fa-check-circle';
    else if (type === 'error') iconClass = 'fas fa-exclamation-circle';
    else if (type === 'warning') iconClass = 'fas fa-exclamation-triangle';
    
    toastIcon.className = `toast-icon ${iconClass}`;
    toastMessage.textContent = message;
    
    // Aplicar clase de tipo
    toast.className = `toast ${type}`;
    
    // Mostrar toast
    toast.classList.add('show');
    
    // Ocultar después de 4 segundos
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Utilidades
function formatNumber(num) {
    return new Intl.NumberFormat('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Manejo de errores globales
window.addEventListener('error', function(event) {
    console.error('Error global:', event.error);
    showToast('Error inesperado en la aplicación', 'error');
});

// Manejo de promesas rechazadas
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promesa rechazada:', event.reason);
    showToast('Error de conexión o datos', 'error');
});

console.log('Script del Servidor de Inventario cargado correctamente');

