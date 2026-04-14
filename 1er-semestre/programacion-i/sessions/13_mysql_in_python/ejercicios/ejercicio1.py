"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 13

EJERCICIO 1 - FILTROS CON MYSQL/SQLite

Crear una aplicacion con filtros de al menos dos variables

APLICACION: Sistema de Consulta de Base de Datos Academica
-----------
Permite filtrar estudiantes, productos y empleados por multiples criterios

CARACTERISTICAS:
- Filtros por 2+ variables simultaneas
- Menu interactivo
- Exportacion de resultados
- Compatible con MySQL y SQLite
"""

import sqlite3
import pandas as pd
import os
import sys
import warnings
from datetime import datetime

# Intentar importar MySQL
try:
    import mysql.connector
    MYSQL_DISPONIBLE = True
except ImportError:
    MYSQL_DISPONIBLE = False

warnings.filterwarnings('ignore')







# ============================================================
# CONFIGURACION
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# Configuracion de base de datos
DB_TYPE = 'sqlite'  # Cambiar a 'mysql' para usar MySQL
DB_FILE = 'DB_Propia.db'

# Configuracion MySQL (si se usa)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'db_propia'
}

# ============================================================
# FUNCIONES DE UTILIDAD
# ============================================================

def crear_separador(titulo, ancho=80):
    """Crea un separador visual"""
    print("\n" + "="*ancho)
    print(titulo.center(ancho))
    print("="*ancho)

def pausar():
    """Pausa hasta que el usuario presione Enter"""
    input("\nPresiona Enter para continuar...")

def limpiar_pantalla():
    """Limpia la pantalla (funciona en Windows, Mac, Linux)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def conectar_db():
    """Conecta a la base de datos"""
    if DB_TYPE == 'mysql' and MYSQL_DISPONIBLE:
        try:
            conexion = mysql.connector.connect(**MYSQL_CONFIG)
            print(f"✓ Conectado a MySQL: {MYSQL_CONFIG['database']}")
            return conexion
        except Exception as e:
            print(f"✗ Error conectando a MySQL: {e}")
            print("  Usando SQLite en su lugar...")
            return sqlite3.connect(DB_FILE)
    else:
        if not os.path.exists(DB_FILE):
            print(f"✗ Error: {DB_FILE} no encontrado")
            print("  Ejecuta primero el ejercicio de la Clase 11")
            sys.exit(1)
        return sqlite3.connect(DB_FILE)

def guardar_resultado(datos, nombre_archivo, columnas):
    """Guarda resultados en CSV"""
    if datos:
        df = pd.DataFrame(datos, columns=columnas)
        ruta = os.path.join(SCRIPT_DIR, nombre_archivo)
        df.to_csv(nombre_archivo, index=False, encoding='utf-8')
        print(f"\n✓ Resultados guardados en: {ruta}")
        return True
    return False

# ============================================================
# FUNCIONES DE FILTRADO - ESTUDIANTES
# ============================================================

def filtrar_estudiantes_por_edad_y_calificacion(cursor):
    """Filtro 1: Estudiantes por rango de edad Y calificacion minima"""
    limpiar_pantalla()
    crear_separador("FILTRO: ESTUDIANTES POR EDAD Y CALIFICACION")
    
    print("\nEste filtro busca estudiantes que cumplan AMBOS criterios:")
    print("  1. Edad dentro de un rango")
    print("  2. Calificacion mayor o igual a un minimo\n")
    
    # Obtener parametros
    try:
        edad_min = int(input("Edad minima (ej: 18): "))
        edad_max = int(input("Edad maxima (ej: 25): "))
        calif_min = int(input("Calificacion minima (ej: 85): "))
    except ValueError:
        print("\n✗ Error: Ingresa numeros validos")
        pausar()
        return
    
    # Ejecutar consulta
    consulta = """
        SELECT nombre, apellido, edad, calificacion, carrera, ciudad
        FROM Estudiantes
        WHERE edad BETWEEN ? AND ?
        AND calificacion >= ?
        ORDER BY calificacion DESC, edad ASC
    """
    
    cursor.execute(consulta, (edad_min, edad_max, calif_min))
    resultados = cursor.fetchall()
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} estudiantes encontrados")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Nombre':<15} {'Apellido':<15} {'Edad':<6} {'Calif':<7} {'Carrera':<25} {'Ciudad':<15}")
        print("-" * 100)
        for row in resultados:
            print(f"{row[0]:<15} {row[1]:<15} {row[2]:<6} {row[3]:<7} {row[4]:<25} {row[5]:<15}")
        
        # Guardar resultados
        if input("\n¿Guardar resultados en CSV? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"estudiantes_edad{edad_min}-{edad_max}_calif{calif_min}_{timestamp}.csv"
            columnas = ['Nombre', 'Apellido', 'Edad', 'Calificacion', 'Carrera', 'Ciudad']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron estudiantes con esos criterios")
    
    pausar()

def filtrar_estudiantes_por_ciudad_y_semestre(cursor):
    """Filtro 2: Estudiantes por ciudad Y semestre"""
    limpiar_pantalla()
    crear_separador("FILTRO: ESTUDIANTES POR CIUDAD Y SEMESTRE")
    
    # Mostrar ciudades disponibles
    cursor.execute("SELECT DISTINCT ciudad FROM Estudiantes ORDER BY ciudad")
    ciudades = [row[0] for row in cursor.fetchall()]
    
    print("\nCiudades disponibles:")
    for i, ciudad in enumerate(ciudades, 1):
        print(f"  {i}. {ciudad}")
    
    # Obtener parametros
    try:
        ciudad_idx = int(input("\nSelecciona ciudad (numero): ")) - 1
        if ciudad_idx < 0 or ciudad_idx >= len(ciudades):
            raise ValueError
        ciudad = ciudades[ciudad_idx]
        
        semestre_min = int(input("Semestre minimo (ej: 1): "))
        semestre_max = int(input("Semestre maximo (ej: 8): "))
    except (ValueError, IndexError):
        print("\n✗ Error: Seleccion invalida")
        pausar()
        return
    
    # Ejecutar consulta
    consulta = """
        SELECT nombre, apellido, edad, calificacion, carrera, semestre
        FROM Estudiantes
        WHERE ciudad = ?
        AND semestre BETWEEN ? AND ?
        ORDER BY semestre ASC, calificacion DESC
    """
    
    cursor.execute(consulta, (ciudad, semestre_min, semestre_max))
    resultados = cursor.fetchall()
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} estudiantes en {ciudad}, semestres {semestre_min}-{semestre_max}")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Nombre':<15} {'Apellido':<15} {'Edad':<6} {'Calif':<7} {'Carrera':<25} {'Sem':<5}")
        print("-" * 100)
        for row in resultados:
            print(f"{row[0]:<15} {row[1]:<15} {row[2]:<6} {row[3]:<7} {row[4]:<25} {row[5]:<5}")
        
        # Estadisticas
        cursor.execute("""
            SELECT AVG(calificacion), COUNT(*)
            FROM Estudiantes
            WHERE ciudad = ? AND semestre BETWEEN ? AND ?
        """, (ciudad, semestre_min, semestre_max))
        promedio, total = cursor.fetchone()
        print(f"\nEstadisticas:")
        print(f"  Calificacion promedio: {promedio:.1f}")
        print(f"  Total de estudiantes: {total}")
        
        # Guardar resultados
        if input("\n¿Guardar resultados en CSV? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"estudiantes_{ciudad}_sem{semestre_min}-{semestre_max}_{timestamp}.csv"
            columnas = ['Nombre', 'Apellido', 'Edad', 'Calificacion', 'Carrera', 'Semestre']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron estudiantes con esos criterios")
    
    pausar()

# ============================================================
# FUNCIONES DE FILTRADO - PRODUCTOS
# ============================================================

def filtrar_productos_por_precio_y_stock(cursor):
    """Filtro 3: Productos por rango de precio Y stock minimo"""
    limpiar_pantalla()
    crear_separador("FILTRO: PRODUCTOS POR PRECIO Y STOCK")
    
    print("\nEste filtro busca productos que cumplan AMBOS criterios:")
    print("  1. Precio dentro de un rango")
    print("  2. Stock mayor o igual a un minimo\n")
    
    # Obtener parametros
    try:
        precio_min = float(input("Precio minimo (ej: 1000): "))
        precio_max = float(input("Precio maximo (ej: 10000): "))
        stock_min = int(input("Stock minimo (ej: 50): "))
    except ValueError:
        print("\n✗ Error: Ingresa numeros validos")
        pausar()
        return
    
    # Ejecutar consulta
    consulta = """
        SELECT nombre, categoria, precio, stock, marca, proveedor
        FROM Productos
        WHERE precio BETWEEN ? AND ?
        AND stock >= ?
        ORDER BY precio ASC, stock DESC
    """
    
    cursor.execute(consulta, (precio_min, precio_max, stock_min))
    resultados = cursor.fetchall()
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} productos encontrados")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Producto':<20} {'Categoria':<15} {'Precio':<10} {'Stock':<8} {'Marca':<15} {'Proveedor':<20}")
        print("-" * 100)
        for row in resultados:
            print(f"{row[0]:<20} {row[1]:<15} ${row[2]:<9,.0f} {row[3]:<8} {row[4]:<15} {row[5]:<20}")
        
        # Estadisticas
        cursor.execute("""
            SELECT SUM(precio * stock), AVG(precio), SUM(stock)
            FROM Productos
            WHERE precio BETWEEN ? AND ? AND stock >= ?
        """, (precio_min, precio_max, stock_min))
        valor_total, precio_prom, stock_total = cursor.fetchone()
        print(f"\nEstadisticas:")
        print(f"  Valor total inventario: ${valor_total:,.2f}")
        print(f"  Precio promedio: ${precio_prom:,.2f}")
        print(f"  Stock total: {stock_total} unidades")
        
        # Guardar resultados
        if input("\n¿Guardar resultados en CSV? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"productos_precio{int(precio_min)}-{int(precio_max)}_stock{stock_min}_{timestamp}.csv"
            columnas = ['Producto', 'Categoria', 'Precio', 'Stock', 'Marca', 'Proveedor']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron productos con esos criterios")
    
    pausar()

def filtrar_productos_por_categoria_y_marca(cursor):
    """Filtro 4: Productos por categoria Y marca"""
    limpiar_pantalla()
    crear_separador("FILTRO: PRODUCTOS POR CATEGORIA Y MARCA")
    
    # Mostrar categorias disponibles
    cursor.execute("SELECT DISTINCT categoria FROM Productos ORDER BY categoria")
    categorias = [row[0] for row in cursor.fetchall()]
    
    print("\nCategorias disponibles:")
    for i, cat in enumerate(categorias, 1):
        print(f"  {i}. {cat}")
    
    # Mostrar marcas disponibles
    cursor.execute("SELECT DISTINCT marca FROM Productos ORDER BY marca")
    marcas = [row[0] for row in cursor.fetchall()]
    
    print("\nMarcas disponibles:")
    for i, marca in enumerate(marcas, 1):
        print(f"  {i}. {marca}")
    
    # Obtener parametros
    try:
        cat_idx = int(input("\nSelecciona categoria (numero): ")) - 1
        if cat_idx < 0 or cat_idx >= len(categorias):
            raise ValueError
        categoria = categorias[cat_idx]
        
        marca_idx = int(input("Selecciona marca (numero): ")) - 1
        if marca_idx < 0 or marca_idx >= len(marcas):
            raise ValueError
        marca = marcas[marca_idx]
    except (ValueError, IndexError):
        print("\n✗ Error: Seleccion invalida")
        pausar()
        return
    
    # Ejecutar consulta
    consulta = """
        SELECT nombre, precio, stock, proveedor, codigo
        FROM Productos
        WHERE categoria = ?
        AND marca = ?
        ORDER BY precio DESC
    """
    
    cursor.execute(consulta, (categoria, marca))
    resultados = cursor.fetchall()
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} productos de {marca} en {categoria}")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Producto':<25} {'Precio':<12} {'Stock':<10} {'Proveedor':<20} {'Codigo':<15}")
        print("-" * 90)
        for row in resultados:
            print(f"{row[0]:<25} ${row[1]:<11,.0f} {row[2]:<10} {row[3]:<20} {row[4]:<15}")
        
        # Guardar resultados
        if input("\n¿Guardar resultados en CSV? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"productos_{categoria}_{marca}_{timestamp}.csv"
            columnas = ['Producto', 'Precio', 'Stock', 'Proveedor', 'Codigo']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print(f"\n✗ No se encontraron productos de {marca} en {categoria}")
    
    pausar()

# ============================================================
# FUNCIONES DE FILTRADO - EMPLEADOS
# ============================================================

def filtrar_empleados_por_salario_y_antiguedad(cursor):
    """Filtro 5: Empleados por rango de salario Y antiguedad minima"""
    limpiar_pantalla()
    crear_separador("FILTRO: EMPLEADOS POR SALARIO Y ANTIGUEDAD")
    
    print("\nEste filtro busca empleados que cumplan AMBOS criterios:")
    print("  1. Salario dentro de un rango")
    print("  2. Antiguedad mayor o igual a un minimo\n")
    
    # Obtener parametros
    try:
        salario_min = float(input("Salario minimo (ej: 20000): "))
        salario_max = float(input("Salario maximo (ej: 50000): "))
        antiguedad_min = int(input("Antiguedad minima en años (ej: 3): "))
    except ValueError:
        print("\n✗ Error: Ingresa numeros validos")
        pausar()
        return
    
    # Ejecutar consulta
    consulta = """
        SELECT nombre, apellido, puesto, salario, departamento, antiguedad, email
        FROM Empleados
        WHERE salario BETWEEN ? AND ?
        AND antiguedad >= ?
        ORDER BY salario DESC, antiguedad DESC
    """
    
    cursor.execute(consulta, (salario_min, salario_max, antiguedad_min))
    resultados = cursor.fetchall()
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} empleados encontrados")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Nombre':<12} {'Apellido':<12} {'Puesto':<20} {'Salario':<12} {'Depto':<15} {'Años':<6}")
        print("-" * 90)
        for row in resultados:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<20} ${row[3]:<11,.0f} {row[4]:<15} {row[5]:<6}")
        
        # Estadisticas
        cursor.execute("""
            SELECT SUM(salario), AVG(salario), AVG(antiguedad)
            FROM Empleados
            WHERE salario BETWEEN ? AND ? AND antiguedad >= ?
        """, (salario_min, salario_max, antiguedad_min))
        nomina_total, salario_prom, antiguedad_prom = cursor.fetchone()
        print(f"\nEstadisticas:")
        print(f"  Nomina total: ${nomina_total:,.2f}")
        print(f"  Salario promedio: ${salario_prom:,.2f}")
        print(f"  Antiguedad promedio: {antiguedad_prom:.1f} años")
        
        # Guardar resultados
        if input("\n¿Guardar resultados en CSV? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"empleados_salario{int(salario_min)}-{int(salario_max)}_antig{antiguedad_min}_{timestamp}.csv"
            columnas = ['Nombre', 'Apellido', 'Puesto', 'Salario', 'Departamento', 'Antiguedad', 'Email']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron empleados con esos criterios")
    
    pausar()

def filtrar_empleados_por_departamento_y_salario(cursor):
    """Filtro 6: Empleados por departamento Y salario minimo"""
    limpiar_pantalla()
    crear_separador("FILTRO: EMPLEADOS POR DEPARTAMENTO Y SALARIO")
    
    # Mostrar departamentos disponibles
    cursor.execute("SELECT DISTINCT departamento FROM Empleados ORDER BY departamento")
    departamentos = [row[0] for row in cursor.fetchall()]
    
    print("\nDepartamentos disponibles:")
    for i, depto in enumerate(departamentos, 1):
        print(f"  {i}. {depto}")
    
    # Obtener parametros
    try:
        depto_idx = int(input("\nSelecciona departamento (numero): ")) - 1
        if depto_idx < 0 or depto_idx >= len(departamentos):
            raise ValueError
        departamento = departamentos[depto_idx]
        
        salario_min = float(input("Salario minimo (ej: 25000): "))
    except (ValueError, IndexError):
        print("\n✗ Error: Seleccion/valor invalido")
        pausar()
        return
    
    # Ejecutar consulta
    consulta = """
        SELECT nombre, apellido, puesto, salario, antiguedad, email
        FROM Empleados
        WHERE departamento = ?
        AND salario >= ?
        ORDER BY salario DESC
    """
    
    cursor.execute(consulta, (departamento, salario_min))
    resultados = cursor.fetchall()
    
    # Mostrar resultados
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} empleados en {departamento} con salario >= ${salario_min:,.0f}")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Nombre':<12} {'Apellido':<12} {'Puesto':<25} {'Salario':<12} {'Años':<6} {'Email':<30}")
        print("-" * 110)
        for row in resultados:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<25} ${row[3]:<11,.0f} {row[4]:<6} {row[5]:<30}")
        
        # Estadisticas del departamento
        cursor.execute("""
            SELECT COUNT(*), AVG(salario), SUM(salario)
            FROM Empleados
            WHERE departamento = ? AND salario >= ?
        """, (departamento, salario_min))
        total, salario_prom, nomina = cursor.fetchone()
        print(f"\nEstadisticas de {departamento}:")
        print(f"  Empleados con salario >= ${salario_min:,.0f}: {total}")
        print(f"  Salario promedio: ${salario_prom:,.2f}")
        print(f"  Nomina parcial: ${nomina:,.2f}")
        
        # Guardar resultados
        if input("\n¿Guardar resultados en CSV? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"empleados_{departamento}_salario{int(salario_min)}_{timestamp}.csv"
            columnas = ['Nombre', 'Apellido', 'Puesto', 'Salario', 'Antiguedad', 'Email']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print(f"\n✗ No se encontraron empleados en {departamento} con ese salario")
    
    pausar()

# ============================================================
# FILTRO AVANZADO COMBINADO
# ============================================================

def filtro_avanzado_multicriterio(cursor):
    """Filtro 7: Busqueda avanzada con multiples criterios opcionales"""
    limpiar_pantalla()
    crear_separador("FILTRO AVANZADO: BUSQUEDA MULTICRITERIO")
    
    print("\nSelecciona la tabla a consultar:")
    print("  1. Estudiantes")
    print("  2. Productos")
    print("  3. Empleados")
    
    try:
        opcion = int(input("\nOpcion: "))
    except ValueError:
        print("\n✗ Error: Opcion invalida")
        pausar()
        return
    
    if opcion == 1:
        filtro_estudiantes_avanzado(cursor)
    elif opcion == 2:
        filtro_productos_avanzado(cursor)
    elif opcion == 3:
        filtro_empleados_avanzado(cursor)
    else:
        print("\n✗ Opcion invalida")
        pausar()

def filtro_estudiantes_avanzado(cursor):
    """Filtro avanzado de estudiantes con 3+ criterios"""
    print("\n--- FILTRO AVANZADO DE ESTUDIANTES ---")
    print("Ingresa los criterios (deja en blanco para omitir):\n")
    
    # Recopilar criterios
    ciudad = input("Ciudad: ").strip()
    edad_min = input("Edad minima: ").strip()
    edad_max = input("Edad maxima: ").strip()
    calif_min = input("Calificacion minima: ").strip()
    semestre_min = input("Semestre minimo: ").strip()
    semestre_max = input("Semestre maximo: ").strip()
    
    # Construir consulta dinamica
    consulta = "SELECT nombre, apellido, edad, calificacion, carrera, semestre, ciudad FROM Estudiantes WHERE 1=1"
    parametros = []
    
    if ciudad:
        consulta += " AND ciudad = ?"
        parametros.append(ciudad)
    if edad_min:
        consulta += " AND edad >= ?"
        parametros.append(int(edad_min))
    if edad_max:
        consulta += " AND edad <= ?"
        parametros.append(int(edad_max))
    if calif_min:
        consulta += " AND calificacion >= ?"
        parametros.append(int(calif_min))
    if semestre_min:
        consulta += " AND semestre >= ?"
        parametros.append(int(semestre_min))
    if semestre_max:
        consulta += " AND semestre <= ?"
        parametros.append(int(semestre_max))
    
    consulta += " ORDER BY calificacion DESC"
    
    # Ejecutar
    cursor.execute(consulta, tuple(parametros))
    resultados = cursor.fetchall()
    
    # Mostrar
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} estudiantes encontrados")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Nombre':<12} {'Apellido':<12} {'Edad':<6} {'Calif':<7} {'Carrera':<20} {'Sem':<5} {'Ciudad':<12}")
        print("-" * 90)
        for row in resultados:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<6} {row[3]:<7} {row[4]:<20} {row[5]:<5} {row[6]:<12}")
        
        if input("\n¿Guardar resultados? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"estudiantes_avanzado_{timestamp}.csv"
            columnas = ['Nombre', 'Apellido', 'Edad', 'Calificacion', 'Carrera', 'Semestre', 'Ciudad']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron estudiantes")
    
    pausar()

def filtro_productos_avanzado(cursor):
    """Filtro avanzado de productos con 3+ criterios"""
    print("\n--- FILTRO AVANZADO DE PRODUCTOS ---")
    print("Ingresa los criterios (deja en blanco para omitir):\n")
    
    categoria = input("Categoria: ").strip()
    marca = input("Marca: ").strip()
    precio_min = input("Precio minimo: ").strip()
    precio_max = input("Precio maximo: ").strip()
    stock_min = input("Stock minimo: ").strip()
    
    # Construir consulta
    consulta = "SELECT nombre, categoria, marca, precio, stock, proveedor FROM Productos WHERE 1=1"
    parametros = []
    
    if categoria:
        consulta += " AND categoria = ?"
        parametros.append(categoria)
    if marca:
        consulta += " AND marca = ?"
        parametros.append(marca)
    if precio_min:
        consulta += " AND precio >= ?"
        parametros.append(float(precio_min))
    if precio_max:
        consulta += " AND precio <= ?"
        parametros.append(float(precio_max))
    if stock_min:
        consulta += " AND stock >= ?"
        parametros.append(int(stock_min))
    
    consulta += " ORDER BY precio DESC"
    
    cursor.execute(consulta, tuple(parametros))
    resultados = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} productos encontrados")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Producto':<20} {'Categoria':<15} {'Marca':<15} {'Precio':<12} {'Stock':<8}")
        print("-" * 80)
        for row in resultados:
            print(f"{row[0]:<20} {row[1]:<15} {row[2]:<15} ${row[3]:<11,.0f} {row[4]:<8}")
        
        if input("\n¿Guardar resultados? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"productos_avanzado_{timestamp}.csv"
            columnas = ['Producto', 'Categoria', 'Marca', 'Precio', 'Stock', 'Proveedor']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron productos")
    
    pausar()

def filtro_empleados_avanzado(cursor):
    """Filtro avanzado de empleados con 3+ criterios"""
    print("\n--- FILTRO AVANZADO DE EMPLEADOS ---")
    print("Ingresa los criterios (deja en blanco para omitir):\n")
    
    departamento = input("Departamento: ").strip()
    salario_min = input("Salario minimo: ").strip()
    salario_max = input("Salario maximo: ").strip()
    antiguedad_min = input("Antiguedad minima (años): ").strip()
    
    # Construir consulta
    consulta = "SELECT nombre, apellido, puesto, salario, departamento, antiguedad FROM Empleados WHERE 1=1"
    parametros = []
    
    if departamento:
        consulta += " AND departamento = ?"
        parametros.append(departamento)
    if salario_min:
        consulta += " AND salario >= ?"
        parametros.append(float(salario_min))
    if salario_max:
        consulta += " AND salario <= ?"
        parametros.append(float(salario_max))
    if antiguedad_min:
        consulta += " AND antiguedad >= ?"
        parametros.append(int(antiguedad_min))
    
    consulta += " ORDER BY salario DESC"
    
    cursor.execute(consulta, tuple(parametros))
    resultados = cursor.fetchall()
    
    print(f"\n{'='*80}")
    print(f"RESULTADOS: {len(resultados)} empleados encontrados")
    print(f"{'='*80}")
    
    if resultados:
        print(f"\n{'Nombre':<12} {'Apellido':<12} {'Puesto':<20} {'Salario':<12} {'Depto':<15} {'Años':<6}")
        print("-" * 90)
        for row in resultados:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<20} ${row[3]:<11,.0f} {row[4]:<15} {row[5]:<6}")
        
        if input("\n¿Guardar resultados? (s/n): ").lower() == 's':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"empleados_avanzado_{timestamp}.csv"
            columnas = ['Nombre', 'Apellido', 'Puesto', 'Salario', 'Departamento', 'Antiguedad']
            guardar_resultado(resultados, archivo, columnas)
    else:
        print("\n✗ No se encontraron empleados")
    
    pausar()

# ============================================================
# MENU PRINCIPAL
# ============================================================

def mostrar_menu():
    """Muestra el menu principal"""
    limpiar_pantalla()
    crear_separador("SISTEMA DE FILTROS - BASE DE DATOS ACADEMICA")
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                        FILTROS DISPONIBLES                                ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ESTUDIANTES:                                                             ║
║    1. Filtrar por EDAD y CALIFICACION                                     ║
║    2. Filtrar por CIUDAD y SEMESTRE                                       ║
║                                                                           ║
║  PRODUCTOS:                                                               ║
║    3. Filtrar por PRECIO y STOCK                                          ║
║    4. Filtrar por CATEGORIA y MARCA                                       ║
║                                                                           ║
║  EMPLEADOS:                                                               ║
║    5. Filtrar por SALARIO y ANTIGUEDAD                                    ║
║    6. Filtrar por DEPARTAMENTO y SALARIO                                  ║
║                                                                           ║
║  AVANZADO:                                                                ║
║    7. Busqueda multicriterio (3+ variables)                               ║
║                                                                           ║
║    8. Ver estadisticas generales                                          ║
║    9. Salir                                                               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)

def ver_estadisticas(cursor):
    """Muestra estadisticas generales de la base de datos"""
    limpiar_pantalla()
    crear_separador("ESTADISTICAS GENERALES")
    
    print("\nESTUDIANTES:")
    cursor.execute("SELECT COUNT(*), AVG(edad), AVG(calificacion) FROM Estudiantes")
    total_est, edad_prom, calif_prom = cursor.fetchone()
    print(f"  Total: {total_est}")
    print(f"  Edad promedio: {edad_prom:.1f} años")
    print(f"  Calificacion promedio: {calif_prom:.1f}")
    
    print("\nPRODUCTOS:")
    cursor.execute("SELECT COUNT(*), SUM(stock), AVG(precio), SUM(precio * stock) FROM Productos")
    total_prod, stock_total, precio_prom, valor_inv = cursor.fetchone()
    print(f"  Total: {total_prod}")
    print(f"  Stock total: {stock_total} unidades")
    print(f"  Precio promedio: ${precio_prom:,.2f}")
    print(f"  Valor inventario: ${valor_inv:,.2f}")
    
    print("\nEMPLEADOS:")
    cursor.execute("SELECT COUNT(*), AVG(salario), AVG(antiguedad), SUM(salario) FROM Empleados")
    total_emp, salario_prom, antig_prom, nomina = cursor.fetchone()
    print(f"  Total: {total_emp}")
    print(f"  Salario promedio: ${salario_prom:,.2f}")
    print(f"  Antiguedad promedio: {antig_prom:.1f} años")
    print(f"  Nomina total: ${nomina:,.2f}")
    
    pausar()

def main():
    """Funcion principal"""
    print("="*80)
    print("SISTEMA DE FILTROS - CLASE 13")
    print("Carlos Pulido Rosas - MCD - CUCEA")
    print("="*80)
    print(f"\nDirectorio: {SCRIPT_DIR}")
    print(f"Base de datos: {DB_TYPE.upper()}")
    if DB_TYPE == 'mysql':
        print(f"MySQL disponible: {'SI' if MYSQL_DISPONIBLE else 'NO (usando SQLite)'}")
    print()
    
    # Conectar a la base de datos
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Menu principal
    while True:
        mostrar_menu()
        try:
            opcion = int(input("Selecciona una opcion: "))
        except ValueError:
            print("\n✗ Error: Ingresa un numero valido")
            pausar()
            continue
        
        if opcion == 1:
            filtrar_estudiantes_por_edad_y_calificacion(cursor)
        elif opcion == 2:
            filtrar_estudiantes_por_ciudad_y_semestre(cursor)
        elif opcion == 3:
            filtrar_productos_por_precio_y_stock(cursor)
        elif opcion == 4:
            filtrar_productos_por_categoria_y_marca(cursor)
        elif opcion == 5:
            filtrar_empleados_por_salario_y_antiguedad(cursor)
        elif opcion == 6:
            filtrar_empleados_por_departamento_y_salario(cursor)
        elif opcion == 7:
            filtro_avanzado_multicriterio(cursor)
        elif opcion == 8:
            ver_estadisticas(cursor)
        elif opcion == 9:
            print("\n¡Hasta luego!")
            break
        else:
            print("\n✗ Opcion invalida")
            pausar()
    
    # Cerrar conexion
    cursor.close()
    conexion.close()

if __name__ == "__main__":
    main()