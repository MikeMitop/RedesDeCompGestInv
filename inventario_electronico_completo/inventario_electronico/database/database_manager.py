"""
Gestor de Base de Datos para Sistema de Inventario Electrónico
Maneja todas las operaciones CRUD para productos, clientes y transacciones
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "inventario.db"):
        """
        Inicializa el gestor de base de datos
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos ejecutando el esquema SQL"""
        try:
            # Leer el esquema SQL
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Ejecutar el esquema
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript(schema_sql)
                conn.commit()
            
            print(f"Base de datos inicializada correctamente: {self.db_path}")
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        return conn
    
    # ==================== OPERACIONES DE PRODUCTOS ====================
    
    def obtener_productos(self, activos_solo: bool = True) -> List[Dict]:
        """
        Obtiene todos los productos
        
        Args:
            activos_solo: Si True, solo devuelve productos activos
            
        Returns:
            Lista de diccionarios con información de productos
        """
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM productos"
                if activos_solo:
                    query += " WHERE activo = 1"
                query += " ORDER BY nombre_producto"
                
                cursor = conn.execute(query)
                productos = [dict(row) for row in cursor.fetchall()]
                return productos
        except Exception as e:
            print(f"Error al obtener productos: {e}")
            return []
    
    def obtener_producto_por_id(self, id_producto: int) -> Optional[Dict]:
        """
        Obtiene un producto específico por ID
        
        Args:
            id_producto: ID del producto a buscar
            
        Returns:
            Diccionario con información del producto o None si no existe
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM productos WHERE id_producto = ?", 
                    (id_producto,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error al obtener producto {id_producto}: {e}")
            return None
    
    def crear_producto(self, nombre: str, cantidad: int, precio: float, 
                      descripcion: str = "", categoria: str = "", 
                      proveedor: str = "") -> int:
        """
        Crea un nuevo producto
        
        Args:
            nombre: Nombre del producto
            cantidad: Cantidad inicial en inventario
            precio: Precio del producto
            descripcion: Descripción opcional
            categoria: Categoría opcional
            proveedor: Proveedor opcional
            
        Returns:
            ID del producto creado
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO productos (nombre_producto, descripcion, cantidad, 
                                         precio, categoria, proveedor)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nombre, descripcion, cantidad, precio, categoria, proveedor))
                
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al crear producto: {e}")
            raise
    
    def actualizar_producto(self, id_producto: int, nombre: str, cantidad: int, 
                           precio: float, descripcion: str = "", 
                           categoria: str = "", proveedor: str = "") -> bool:
        """
        Actualiza un producto existente
        
        Args:
            id_producto: ID del producto a actualizar
            nombre: Nuevo nombre del producto
            cantidad: Nueva cantidad
            precio: Nuevo precio
            descripcion: Nueva descripción
            categoria: Nueva categoría
            proveedor: Nuevo proveedor
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    UPDATE productos 
                    SET nombre_producto = ?, descripcion = ?, cantidad = ?, 
                        precio = ?, categoria = ?, proveedor = ?
                    WHERE id_producto = ?
                """, (nombre, descripcion, cantidad, precio, categoria, 
                      proveedor, id_producto))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar producto {id_producto}: {e}")
            return False
    
    def eliminar_producto(self, id_producto: int) -> bool:
        """
        Elimina (desactiva) un producto
        
        Args:
            id_producto: ID del producto a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE productos SET activo = 0 WHERE id_producto = ?",
                    (id_producto,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar producto {id_producto}: {e}")
            return False
    
    # ==================== OPERACIONES DE CLIENTES ====================
    
    def obtener_clientes(self, activos_solo: bool = True) -> List[Dict]:
        """
        Obtiene todos los clientes
        
        Args:
            activos_solo: Si True, solo devuelve clientes activos
            
        Returns:
            Lista de diccionarios con información de clientes
        """
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM clientes"
                if activos_solo:
                    query += " WHERE activo = 1"
                query += " ORDER BY nombre_cliente"
                
                cursor = conn.execute(query)
                clientes = [dict(row) for row in cursor.fetchall()]
                return clientes
        except Exception as e:
            print(f"Error al obtener clientes: {e}")
            return []
    
    def crear_cliente(self, nombre: str, email: str = "", telefono: str = "", 
                     direccion: str = "") -> int:
        """
        Crea un nuevo cliente
        
        Args:
            nombre: Nombre del cliente
            email: Email opcional
            telefono: Teléfono opcional
            direccion: Dirección opcional
            
        Returns:
            ID del cliente creado
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO clientes (nombre_cliente, email, telefono, direccion)
                    VALUES (?, ?, ?, ?)
                """, (nombre, email, telefono, direccion))
                
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            raise
    
    # ==================== OPERACIONES DE TRANSACCIONES ====================
    
    def registrar_transaccion(self, id_producto: int, tipo: str, cantidad: int,
                             id_cliente: int = None, precio_unitario: float = None,
                             observaciones: str = "") -> int:
        """
        Registra una transacción de inventario
        
        Args:
            id_producto: ID del producto
            tipo: Tipo de transacción ('entrada', 'salida', 'ajuste')
            cantidad: Cantidad de la transacción
            id_cliente: ID del cliente (opcional)
            precio_unitario: Precio unitario (opcional)
            observaciones: Observaciones adicionales
            
        Returns:
            ID de la transacción creada
        """
        try:
            with self.get_connection() as conn:
                # Calcular total si se proporciona precio unitario
                total = (precio_unitario * cantidad) if precio_unitario else None
                
                cursor = conn.execute("""
                    INSERT INTO transacciones 
                    (id_producto, id_cliente, tipo_transaccion, cantidad, 
                     precio_unitario, total, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (id_producto, id_cliente, tipo, cantidad, 
                      precio_unitario, total, observaciones))
                
                # Actualizar cantidad en inventario según el tipo de transacción
                if tipo == 'entrada':
                    conn.execute("""
                        UPDATE productos 
                        SET cantidad = cantidad + ? 
                        WHERE id_producto = ?
                    """, (cantidad, id_producto))
                elif tipo == 'salida':
                    conn.execute("""
                        UPDATE productos 
                        SET cantidad = cantidad - ? 
                        WHERE id_producto = ?
                    """, (cantidad, id_producto))
                elif tipo == 'ajuste':
                    conn.execute("""
                        UPDATE productos 
                        SET cantidad = ? 
                        WHERE id_producto = ?
                    """, (cantidad, id_producto))
                
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al registrar transacción: {e}")
            raise
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas generales del inventario
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # Total de productos activos
                cursor = conn.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
                stats['total_productos'] = cursor.fetchone()[0]
                
                # Total de clientes activos
                cursor = conn.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
                stats['total_clientes'] = cursor.fetchone()[0]
                
                # Valor total del inventario
                cursor = conn.execute("""
                    SELECT SUM(cantidad * precio) 
                    FROM productos 
                    WHERE activo = 1
                """)
                result = cursor.fetchone()[0]
                stats['valor_inventario'] = result if result else 0
                
                # Productos con stock bajo (menos de 10 unidades)
                cursor = conn.execute("""
                    SELECT COUNT(*) 
                    FROM productos 
                    WHERE activo = 1 AND cantidad < 10
                """)
                stats['productos_stock_bajo'] = cursor.fetchone()[0]
                
                return stats
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}

# Función de utilidad para inicializar la base de datos
def inicializar_base_datos(db_path: str = "inventario.db") -> DatabaseManager:
    """
    Función de utilidad para inicializar la base de datos
    
    Args:
        db_path: Ruta al archivo de base de datos
        
    Returns:
        Instancia del DatabaseManager
    """
    return DatabaseManager(db_path)

if __name__ == "__main__":
    # Prueba básica del gestor de base de datos
    db = DatabaseManager("test_inventario.db")
    
    # Obtener productos
    productos = db.obtener_productos()
    print(f"Productos encontrados: {len(productos)}")
    
    # Obtener estadísticas
    stats = db.obtener_estadisticas()
    print(f"Estadísticas: {stats}")

