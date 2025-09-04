// JavaScript para el Cliente de Inventario - Máquina 2

// Variables globales
let socket;
let productos = [];
let activityLog = [];
let editingProduct = null;

// Configuración
const SERVIDOR_URL = 'http://localhost:5000';

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Inicializar la aplicación
function initializeApp() {
    console.log('Inicializando Cliente de Inventario...');
    
    // Conectar Socket.IO
    connectSocket();
    
    // Configurar eventos del formulario
    setupFormEvents();
    
    // Verificar estado del servidor
    verificarEstadoServidor();
    
    // Agregar log inicial
    addActivityLog('Cliente iniciado', 'create');
}

// Conectar Socket.IO
function connectSocket() {
    // Conectar al servidor Socket.IO local
    socket = io();
    
    // Eventos de conexión
    socket.on('connect', function() {
        console.log('Conectado al cliente Socket.IO');
        updateConnectionStatus('connected', 'Conectado');
        showToast('Cliente conectado', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Desconectado del cliente Socket.IO');
        updateConnectionStatus('disconnected', 'Desconectado');
        showToast('Cliente desconectado', 'warning');
    });
    
    socket.on('connect_error', function(error) {
        console.error('Error de conexión cliente:', error);
        updateConnectionStatus('disconnected', 'Error de conexión');
        showToast('Error de conexión del cliente', 'error');
    });
    
    // Eventos específicos del cliente
    socket.on('cliente_conectado', function(data) {
        console.log('Cliente conectado:', data);
        addActivityLog('Conectado al sistema cliente', 'create');
    });
    
    socket.on('test_resultado', function(data) {
        console.log('Resultado de prueba del servidor:', data);
        if (data.success) {
            updateServerStatus('connected', 'Servidor disponible');
            showToast('Conexión con servidor exitosa', 'success');
            addActivityLog('Conexión con servidor verificada', 'create');
        } else {
            updateServerStatus('disconnected', 'Servidor no disponible');
            showToast(data.mensaje || 'Error de conexión con servidor', 'error');
            addActivityLog('Error de conexión con servidor', 'error');
        }
    });
}

// Configurar eventos del formulario
function setupFormEvents() {
    const productForm = document.getElementById('productForm');
    const editForm = document.getElementById('editForm');
    
    if (productForm) {
        productForm.addEventListener('submit', handleProductSubmit);
    }
    
    if (editForm) {
        editForm.addEventListener('submit', handleEditSubmit);
    }
}

// Manejar envío del formulario de producto
async function handleProductSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const productData = {
        nombre_producto: formData.get('nombre_producto'),
        cantidad: parseInt(formData.get('cantidad')),
        precio: parseFloat(formData.get('precio')),
        descripcion: formData.get('descripcion') || '',
        categoria: formData.get('categoria') || '',
        proveedor: formData.get('proveedor') || ''
    };
    
    // Validar datos
    if (!productData.nombre_producto || productData.cantidad < 0 || productData.precio < 0) {
        showToast('Por favor completa todos los campos requeridos', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/productos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.mensaje || 'Producto enviado exitosamente', 'success');
            addActivityLog(`Producto creado: ${productData.nombre_producto}`, 'create');
            limpiarFormulario();
            
            // Actualizar lista de productos si está visible
            if (productos.length > 0) {
                setTimeout(cargarProductosServidor, 1000);
            }
        } else {
            showToast(result.error || 'Error al enviar producto', 'error');
            addActivityLog(`Error al crear producto: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error enviando producto:', error);
        showToast('Error de comunicación con el servidor', 'error');
        addActivityLog(`Error de comunicación: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Manejar envío del formulario de edición
async function handleEditSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const productData = {
        nombre_producto: formData.get('nombre_producto'),
        cantidad: parseInt(formData.get('cantidad')),
        precio: parseFloat(formData.get('precio')),
        descripcion: formData.get('descripcion') || '',
        categoria: formData.get('categoria') || '',
        proveedor: formData.get('proveedor') || ''
    };
    
    const productId = formData.get('id_producto');
    
    showLoading();
    
    try {
        const response = await fetch(`/api/productos/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.mensaje || 'Producto actualizado exitosamente', 'success');
            addActivityLog(`Producto actualizado: ${productData.nombre_producto}`, 'update');
            cerrarModalEdicion();
            
            // Actualizar lista de productos
            setTimeout(cargarProductosServidor, 1000);
        } else {
            showToast(result.error || 'Error al actualizar producto', 'error');
            addActivityLog(`Error al actualizar producto: ${result.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error actualizando producto:', error);
        showToast('Error de comunicación con el servidor', 'error');
        addActivityLog(`Error de comunicación: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Verificar estado del servidor
async function verificarEstadoServidor() {
    try {
        const response = await fetch(`${SERVIDOR_URL}/api/status`, {
            method: 'GET',
            timeout: 5000
        });
        
        if (response.ok) {
            const data = await response.json();
            updateServerStatus('connected', 'Servidor disponible');
            addActivityLog('Servidor de inventario disponible', 'create');
        } else {
            updateServerStatus('disconnected', 'Servidor no responde');
            addActivityLog('Servidor de inventario no responde', 'error');
        }
    } catch (error) {
        updateServerStatus('disconnected', 'Error de conexión');
        addActivityLog('Error conectando al servidor de inventario', 'error');
    }
}

// Probar conexión con el servidor
function probarConexionServidor() {
    if (socket && socket.connected) {
        socket.emit('test_servidor');
        addActivityLog('Probando conexión con servidor...', 'update');
    } else {
        verificarEstadoServidor();
    }
}

// Cargar productos del servidor
async function cargarProductosServidor() {
    showLoading();
    
    try {
        const response = await fetch('/api/productos/servidor');
        const result = await response.json();
        
        if (result.success) {
            productos = result.productos || [];
            mostrarProductos();
            showToast(`${productos.length} productos cargados`, 'success');
            addActivityLog(`Cargados ${productos.length} productos del servidor`, 'update');
        } else {
            showToast(result.error || 'Error al cargar productos', 'error');
            addActivityLog('Error al cargar productos del servidor', 'error');
        }
        
    } catch (error) {
        console.error('Error cargando productos:', error);
        showToast('Error de comunicación con el servidor', 'error');
        addActivityLog(`Error cargando productos: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Mostrar productos en la interfaz
function mostrarProductos() {
    const container = document.getElementById('productsContainer');
    const countElement = document.getElementById('productsCount');
    
    if (!container) return;
    
    // Actualizar contador
    if (countElement) {
        countElement.textContent = `${productos.length} productos`;
    }
    
    if (productos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-box-open"></i>
                <p>No hay productos en el servidor</p>
            </div>
        `;
        return;
    }
    
    const productsGrid = document.createElement('div');
    productsGrid.className = 'products-grid';
    
    productos.forEach(producto => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        
        productCard.innerHTML = `
            <div class="product-header">
                <div>
                    <div class="product-title">${escapeHtml(producto.nombre_producto)}</div>
                    <div class="product-id">ID: ${producto.id_producto}</div>
                </div>
                <div class="product-actions">
                    <button class="btn btn-primary btn-icon" onclick="editarProducto(${producto.id_producto})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </div>
            
            <div class="product-details">
                <div class="product-detail">
                    <label>Cantidad</label>
                    <span>${producto.cantidad}</span>
                </div>
                <div class="product-detail">
                    <label>Precio</label>
                    <span>$${formatNumber(producto.precio)}</span>
                </div>
                <div class="product-detail">
                    <label>Categoría</label>
                    <span>${escapeHtml(producto.categoria || 'Sin categoría')}</span>
                </div>
                <div class="product-detail">
                    <label>Proveedor</label>
                    <span>${escapeHtml(producto.proveedor || 'Sin proveedor')}</span>
                </div>
            </div>
            
            ${producto.descripcion ? `
                <div class="product-description">
                    ${escapeHtml(producto.descripcion)}
                </div>
            ` : ''}
        `;
        
        productsGrid.appendChild(productCard);
    });
    
    container.innerHTML = '';
    container.appendChild(productsGrid);
}

// Editar producto
function editarProducto(id) {
    const producto = productos.find(p => p.id_producto === id);
    if (!producto) {
        showToast('Producto no encontrado', 'error');
        return;
    }
    
    editingProduct = producto;
    
    // Llenar formulario de edición
    document.getElementById('editId').value = producto.id_producto;
    document.getElementById('editNombre').value = producto.nombre_producto;
    document.getElementById('editCantidad').value = producto.cantidad;
    document.getElementById('editPrecio').value = producto.precio;
    document.getElementById('editCategoria').value = producto.categoria || '';
    document.getElementById('editProveedor').value = producto.proveedor || '';
    document.getElementById('editDescripcion').value = producto.descripcion || '';
    
    // Mostrar modal
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.classList.add('show');
    }
}

// Cerrar modal de edición
function cerrarModalEdicion() {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.classList.remove('show');
    }
    editingProduct = null;
}

// Limpiar formulario
function limpiarFormulario() {
    const form = document.getElementById('productForm');
    if (form) {
        form.reset();
        showToast('Formulario limpiado', 'success');
        addActivityLog('Formulario limpiado', 'update');
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

// Actualizar estado del servidor
function updateServerStatus(status, text) {
    const statusText = document.getElementById('serverStatusText');
    const statusIndicator = document.getElementById('serverStatusIndicator');
    
    if (statusText) {
        statusText.textContent = text;
    }
    
    if (statusIndicator) {
        statusIndicator.className = `status-indicator-small ${status}`;
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

// Cerrar modal al hacer clic fuera
document.addEventListener('click', function(event) {
    const modal = document.getElementById('editModal');
    if (modal && event.target === modal) {
        cerrarModalEdicion();
    }
});

// Cerrar modal con tecla Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarModalEdicion();
    }
});

// Manejo de errores globales
window.addEventListener('error', function(event) {
    console.error('Error global:', event.error);
    showToast('Error inesperado en la aplicación', 'error');
    addActivityLog('Error inesperado: ' + event.error.message, 'error');
});

// Manejo de promesas rechazadas
window.addEventListener('unhandledrejection', function(event) {
    console.error('Promesa rechazada:', event.reason);
    showToast('Error de conexión o datos', 'error');
    addActivityLog('Error de promesa: ' + event.reason, 'error');
});

console.log('Script del Cliente de Inventario cargado correctamente');

