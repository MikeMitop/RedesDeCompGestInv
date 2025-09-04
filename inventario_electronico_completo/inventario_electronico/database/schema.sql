-- Esquema de Base de Datos para Sistema de Inventario Electrónico
-- Creado para el proyecto de inventario distribuido

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_cliente TEXT NOT NULL,
    email TEXT UNIQUE,
    telefono TEXT,
    direccion TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto TEXT NOT NULL,
    descripcion TEXT,
    cantidad INTEGER NOT NULL DEFAULT 0,
    precio DECIMAL(10,2) NOT NULL,
    categoria TEXT,
    proveedor TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT 1
);

-- Tabla de Transacciones (para registrar movimientos de inventario)
CREATE TABLE IF NOT EXISTS transacciones (
    id_transaccion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    id_cliente INTEGER,
    tipo_transaccion TEXT NOT NULL CHECK (tipo_transaccion IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2),
    total DECIMAL(10,2),
    fecha_transaccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre_producto);
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);
CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha_transaccion);
CREATE INDEX IF NOT EXISTS idx_transacciones_producto ON transacciones(id_producto);

-- Trigger para actualizar fecha_actualizacion en productos
CREATE TRIGGER IF NOT EXISTS actualizar_fecha_producto
    AFTER UPDATE ON productos
    FOR EACH ROW
BEGIN
    UPDATE productos SET fecha_actualizacion = CURRENT_TIMESTAMP WHERE id_producto = NEW.id_producto;
END;

-- Datos de ejemplo para pruebas
INSERT OR IGNORE INTO clientes (nombre_cliente, email, telefono, direccion) VALUES
('Juan Pérez', 'juan.perez@email.com', '555-0101', 'Calle Principal 123'),
('María García', 'maria.garcia@email.com', '555-0102', 'Avenida Central 456'),
('Carlos López', 'carlos.lopez@email.com', '555-0103', 'Plaza Mayor 789');

INSERT OR IGNORE INTO productos (nombre_producto, descripcion, cantidad, precio, categoria, proveedor) VALUES
('Smartphone Galaxy', 'Teléfono inteligente de última generación', 25, 599.99, 'Electrónicos', 'Samsung'),
('Laptop Dell', 'Computadora portátil para trabajo y estudio', 15, 899.99, 'Computadoras', 'Dell'),
('Auriculares Bluetooth', 'Auriculares inalámbricos con cancelación de ruido', 50, 149.99, 'Accesorios', 'Sony'),
('Tablet iPad', 'Tablet de 10 pulgadas para entretenimiento', 20, 449.99, 'Electrónicos', 'Apple'),
('Mouse Inalámbrico', 'Mouse ergonómico para oficina', 75, 29.99, 'Accesorios', 'Logitech');

