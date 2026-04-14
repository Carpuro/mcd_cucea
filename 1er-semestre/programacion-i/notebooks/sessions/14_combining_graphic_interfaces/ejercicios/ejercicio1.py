"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 14

EJERCICIO 1 - FILTROS CON MYSQL/SQLite

VERSION 1: Filtros basicos por multiples criterios

VERSION 2: Agregada busqueda por texto (LIKE)
MODIFICACION 1:
- Nuevo filtro: Buscar estudiantes/productos/empleados por nombre
- Usa operador LIKE para busqueda parcial
- Insensible a mayusculas/minusculas

VERSION 3: Agregados graficos estadisticos
MODIFICACION 2:
- Nuevas visualizaciones con matplotlib
- Graficos de barras y pie charts
- Comparativas visuales de datos
- Exportacion de graficos a PNG

APLICACION: Sistema de Consulta de Base de Datos Academica
-----------
Permite filtrar estudiantes, productos y empleados por multiples criterios

CARACTERISTICAS:
- Filtros por 2+ variables simultaneas
- Menu interactivo
- Exportacion de resultados
- Compatible con MySQL y SQLite
- NUEVO: Busqueda por texto con LIKE
"""

import sqlite3
import pandas as pd
import os
import sys
import warnings
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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
DB_TYPE = 'sqlite'  # Cambiar a 'mysql' si tienes servidor MySQL
DB_FILE = 'DB_Propia.db'

# Configuracion MySQL (si se usa)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'db_propia'
}

# VERSION INFO
VERSION = "3.0 - Graficos estadisticos agregados"
FECHA_VERSION = "2025-11-28"

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
# MODIFICACION 1: BUSQUEDA POR TEXTO (DE V2)
# ============================================================

def buscar_por_nombre(cursor):
    """Buscar registros por nombre usando LIKE"""
    limpiar_pantalla()
    crear_separador("BUSQUEDA POR NOMBRE")
    
    print("\nSelecciona la tabla a buscar:")
    print("  1. Estudiantes")
    print("  2. Productos")
    print("  3. Empleados")
    
    try:
        opcion = int(input("\nOpcion: "))
    except ValueError:
        print("\n✗ Error: Opcion invalida")
        pausar()
        return
    
    termino = input("\nIngresa el termino a buscar: ").strip()
    if not termino:
        print("\n✗ Debes ingresar un termino")
        pausar()
        return
    
    patron = f"%{termino}%"
    
    if opcion == 1:
        cursor.execute("""
            SELECT nombre, apellido, edad, calificacion, carrera, ciudad
            FROM Estudiantes
            WHERE LOWER(nombre) LIKE LOWER(?) OR LOWER(apellido) LIKE LOWER(?)
        """, (patron, patron))
        resultados = cursor.fetchall()
        print(f"\n{len(resultados)} estudiantes encontrados")
        for row in resultados:
            print(f"  {row[0]} {row[1]} - {row[4]} - {row[5]}")
    elif opcion == 2:
        cursor.execute("""
            SELECT nombre, categoria, precio, stock
            FROM Productos
            WHERE LOWER(nombre) LIKE LOWER(?)
        """, (patron,))
        resultados = cursor.fetchall()
        print(f"\n{len(resultados)} productos encontrados")
        for row in resultados:
            print(f"  {row[0]} - ${row[2]:,.0f}")
    elif opcion == 3:
        cursor.execute("""
            SELECT nombre, apellido, puesto, departamento
            FROM Empleados
            WHERE LOWER(nombre) LIKE LOWER(?) OR LOWER(apellido) LIKE LOWER(?)
        """, (patron, patron))
        resultados = cursor.fetchall()
        print(f"\n{len(resultados)} empleados encontrados")
        for row in resultados:
            print(f"  {row[0]} {row[1]} - {row[2]} - {row[3]}")
    
    pausar()

# ============================================================
# MODIFICACION 2: NUEVAS FUNCIONES - GRAFICOS ESTADISTICOS
# ============================================================

def generar_graficos(cursor):
    """NUEVO: Menu de graficos estadisticos"""
    limpiar_pantalla()
    crear_separador("GRAFICOS ESTADISTICOS (NUEVO EN V3)")
    
    print("\nSelecciona el tipo de grafico:")
    print("  1. Estudiantes por ciudad (Barras)")
    print("  2. Distribucion de calificaciones (Histograma)")
    print("  3. Productos por categoria (Pie Chart)")
    print("  4. Salarios por departamento (Barras)")
    print("  5. Comparativa general (Multiple)")
    
    try:
        opcion = int(input("\nOpcion: "))
    except ValueError:
        print("\n✗ Error: Opcion invalida")
        pausar()
        return
    
    if opcion == 1:
        grafico_estudiantes_por_ciudad(cursor)
    elif opcion == 2:
        grafico_distribucion_calificaciones(cursor)
    elif opcion == 3:
        grafico_productos_por_categoria(cursor)
    elif opcion == 4:
        grafico_salarios_por_departamento(cursor)
    elif opcion == 5:
        grafico_comparativa_general(cursor)
    else:
        print("\n✗ Opcion invalida")
        pausar()

def grafico_estudiantes_por_ciudad(cursor):
    """Grafico de barras: Estudiantes por ciudad"""
    print("\n[Generando grafico de estudiantes por ciudad...]")
    
    cursor.execute("""
        SELECT ciudad, COUNT(*) as total
        FROM Estudiantes
        GROUP BY ciudad
        ORDER BY total DESC
    """)
    datos = cursor.fetchall()
    
    if not datos:
        print("✗ No hay datos para graficar")
        pausar()
        return
    
    ciudades = [row[0] for row in datos]
    totales = [row[1] for row in datos]
    
    plt.figure(figsize=(10, 6))
    colores = plt.cm.viridis(np.linspace(0.2, 0.9, len(ciudades)))
    barras = plt.bar(ciudades, totales, color=colores, edgecolor='black', linewidth=1.2)
    
    plt.xlabel('Ciudad', fontsize=12, fontweight='bold')
    plt.ylabel('Numero de Estudiantes', fontsize=12, fontweight='bold')
    plt.title('Estudiantes por Ciudad', fontsize=14, fontweight='bold', pad=15)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Valores sobre barras
    for barra in barras:
        altura = barra.get_height()
        plt.text(barra.get_x() + barra.get_width()/2., altura,
                f'{int(altura)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"grafico_estudiantes_ciudad_{timestamp}.png"
    plt.savefig(archivo, dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafico guardado: {archivo}")
    plt.show()
    pausar()

def grafico_distribucion_calificaciones(cursor):
    """Histograma: Distribucion de calificaciones"""
    print("\n[Generando histograma de calificaciones...]")
    
    cursor.execute("SELECT calificacion FROM Estudiantes")
    calificaciones = [row[0] for row in cursor.fetchall()]
    
    if not calificaciones:
        print("✗ No hay datos para graficar")
        pausar()
        return
    
    plt.figure(figsize=(10, 6))
    n, bins, patches = plt.hist(calificaciones, bins=8, color='#3498db', 
                                edgecolor='black', alpha=0.75, linewidth=1.2)
    
    plt.xlabel('Calificacion', fontsize=12, fontweight='bold')
    plt.ylabel('Frecuencia', fontsize=12, fontweight='bold')
    plt.title('Distribucion de Calificaciones', fontsize=14, fontweight='bold', pad=15)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Linea de promedio
    promedio = np.mean(calificaciones)
    plt.axvline(promedio, color='red', linestyle='--', linewidth=2.5,
               label=f'Promedio: {promedio:.1f}')
    plt.legend()
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"grafico_calificaciones_{timestamp}.png"
    plt.savefig(archivo, dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafico guardado: {archivo}")
    plt.show()
    pausar()

def grafico_productos_por_categoria(cursor):
    """Pie chart: Productos por categoria"""
    print("\n[Generando pie chart de productos...]")
    
    cursor.execute("""
        SELECT categoria, COUNT(*) as total
        FROM Productos
        GROUP BY categoria
    """)
    datos = cursor.fetchall()
    
    if not datos:
        print("✗ No hay datos para graficar")
        pausar()
        return
    
    categorias = [row[0] for row in datos]
    totales = [row[1] for row in datos]
    
    plt.figure(figsize=(10, 8))
    colores = plt.cm.Set3(np.linspace(0, 1, len(categorias)))
    explode = [0.05] * len(categorias)
    
    plt.pie(totales, labels=categorias, autopct='%1.1f%%',
           startangle=90, colors=colores, explode=explode,
           shadow=True, textprops={'fontsize': 11, 'fontweight': 'bold'})
    
    plt.title('Distribucion de Productos por Categoria', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"grafico_productos_categoria_{timestamp}.png"
    plt.savefig(archivo, dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafico guardado: {archivo}")
    plt.show()
    pausar()

def grafico_salarios_por_departamento(cursor):
    """Grafico de barras: Salario promedio por departamento"""
    print("\n[Generando grafico de salarios...]")
    
    cursor.execute("""
        SELECT departamento, AVG(salario) as promedio
        FROM Empleados
        GROUP BY departamento
        ORDER BY promedio DESC
    """)
    datos = cursor.fetchall()
    
    if not datos:
        print("✗ No hay datos para graficar")
        pausar()
        return
    
    departamentos = [row[0] for row in datos]
    salarios = [row[1] for row in datos]
    
    plt.figure(figsize=(12, 6))
    colores = plt.cm.plasma(np.linspace(0.2, 0.9, len(departamentos)))
    barras = plt.barh(departamentos, salarios, color=colores, 
                     edgecolor='black', linewidth=1.2)
    
    plt.xlabel('Salario Promedio ($)', fontsize=12, fontweight='bold')
    plt.ylabel('Departamento', fontsize=12, fontweight='bold')
    plt.title('Salario Promedio por Departamento', fontsize=14, fontweight='bold', pad=15)
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Valores en las barras
    for i, barra in enumerate(barras):
        ancho = barra.get_width()
        plt.text(ancho, barra.get_y() + barra.get_height()/2.,
                f'${ancho:,.0f}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"grafico_salarios_departamento_{timestamp}.png"
    plt.savefig(archivo, dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafico guardado: {archivo}")
    plt.show()
    pausar()

def grafico_comparativa_general(cursor):
    """Grafico multiple: Comparativa general"""
    print("\n[Generando grafico comparativo...]")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Grafico 1: Estudiantes por ciudad
    cursor.execute("SELECT ciudad, COUNT(*) FROM Estudiantes GROUP BY ciudad")
    datos = cursor.fetchall()
    ciudades = [row[0] for row in datos]
    totales = [row[1] for row in datos]
    ax1.bar(ciudades, totales, color='#3498db', edgecolor='black')
    ax1.set_title('Estudiantes por Ciudad', fontweight='bold')
    ax1.set_ylabel('Cantidad')
    ax1.tick_params(axis='x', rotation=45)
    
    # Grafico 2: Calificaciones
    cursor.execute("SELECT calificacion FROM Estudiantes")
    califs = [row[0] for row in cursor.fetchall()]
    ax2.hist(califs, bins=8, color='#2ecc71', edgecolor='black', alpha=0.7)
    ax2.set_title('Distribucion de Calificaciones', fontweight='bold')
    ax2.set_xlabel('Calificacion')
    ax2.set_ylabel('Frecuencia')
    
    # Grafico 3: Productos por categoria
    cursor.execute("SELECT categoria, COUNT(*) FROM Productos GROUP BY categoria")
    datos = cursor.fetchall()
    categorias = [row[0] for row in datos]
    totales = [row[1] for row in datos]
    ax3.pie(totales, labels=categorias, autopct='%1.1f%%', startangle=90)
    ax3.set_title('Productos por Categoria', fontweight='bold')
    
    # Grafico 4: Salarios
    cursor.execute("SELECT departamento, AVG(salario) FROM Empleados GROUP BY departamento")
    datos = cursor.fetchall()
    deptos = [row[0] for row in datos]
    salarios = [row[1] for row in datos]
    ax4.barh(deptos, salarios, color='#e74c3c', edgecolor='black')
    ax4.set_title('Salario Promedio por Depto', fontweight='bold')
    ax4.set_xlabel('Salario ($)')
    
    plt.suptitle('Dashboard Estadistico General', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = f"grafico_dashboard_{timestamp}.png"
    plt.savefig(archivo, dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafico guardado: {archivo}")
    plt.show()
    pausar()

# ============================================================
# MENU PRINCIPAL (MODIFICADO)
# ============================================================

def mostrar_menu():
    """Muestra el menu principal - ACTUALIZADO V3"""
    limpiar_pantalla()
    crear_separador("SISTEMA DE FILTROS - BASE DE DATOS ACADEMICA")
    
    print(f"\nVERSION: {VERSION}")
    print(f"Fecha: {FECHA_VERSION}")
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                        MENU PRINCIPAL                                     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  🔍 BUSQUEDA:                                                             ║
║    1. Buscar por nombre (V2)                                              ║
║                                                                           ║
║  📊 GRAFICOS: ⭐ NUEVA FUNCIONALIDAD V3                                   ║
║    2. Generar graficos estadisticos                                       ║
║                                                                           ║
║  📈 ESTADISTICAS:                                                         ║
║    3. Ver estadisticas generales                                          ║
║                                                                           ║
║    4. Salir                                                               ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)

def ver_estadisticas(cursor):
    """Muestra estadisticas generales"""
    limpiar_pantalla()
    crear_separador("ESTADISTICAS GENERALES")
    
    print("\nESTUDIANTES:")
    cursor.execute("SELECT COUNT(*), AVG(edad), AVG(calificacion) FROM Estudiantes")
    total_est, edad_prom, calif_prom = cursor.fetchone()
    print(f"  Total: {total_est}")
    print(f"  Edad promedio: {edad_prom:.1f} años")
    print(f"  Calificacion promedio: {calif_prom:.1f}")
    
    print("\nPRODUCTOS:")
    cursor.execute("SELECT COUNT(*), SUM(stock), AVG(precio) FROM Productos")
    total_prod, stock_total, precio_prom = cursor.fetchone()
    print(f"  Total: {total_prod}")
    print(f"  Stock total: {stock_total} unidades")
    print(f"  Precio promedio: ${precio_prom:,.2f}")
    
    print("\nEMPLEADOS:")
    cursor.execute("SELECT COUNT(*), AVG(salario), SUM(salario) FROM Empleados")
    total_emp, salario_prom, nomina = cursor.fetchone()
    print(f"  Total: {total_emp}")
    print(f"  Salario promedio: ${salario_prom:,.2f}")
    print(f"  Nomina total: ${nomina:,.2f}")
    
    pausar()

def main():
    """Funcion principal"""
    print("="*80)
    print("SISTEMA DE FILTROS - CLASE 13 - VERSION 3")
    print("Carlos Pulido Rosas - MCD - CUCEA")
    print("="*80)
    print(f"\nVersion: {VERSION}")
    print(f"Directorio: {SCRIPT_DIR}")
    print(f"Base de datos: {DB_TYPE.upper()}")
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
            buscar_por_nombre(cursor)
        elif opcion == 2:
            generar_graficos(cursor)  # NUEVA FUNCION V3
        elif opcion == 3:
            ver_estadisticas(cursor)
        elif opcion == 4:
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