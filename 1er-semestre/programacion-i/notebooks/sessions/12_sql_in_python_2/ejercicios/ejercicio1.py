"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 12

EJERCICIO 1 - SQL EN PYTHON 2 (MySQL)

Aplicar funciones SQL avanzadas en la base de datos creada en la Clase 11

DRIVER MYSQL:
-------------
Para conectarnos a MySQL desde Python, utilizamos el driver 'mysql-connector-python'

INSTALACION:
    pip install mysql-connector-python
    
    O con conda:
    conda install -c conda-forge mysql-connector-python

FUNCIONES SQL A APLICAR:
-------------------------
1. COUNT() - Contar registros
2. SUM() - Sumar valores
3. AVG() - Promedio
4. MIN() - Valor minimo
5. MAX() - Valor maximo
6. GROUP BY - Agrupar datos
7. HAVING - Filtrar grupos
8. ORDER BY - Ordenar resultados
9. LIMIT - Limitar resultados
10. JOIN - Unir tablas (si aplica)

"""

import sqlite3
try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_DISPONIBLE = True
except ImportError:
    MYSQL_DISPONIBLE = False
    print("NOTA: mysql-connector-python no esta instalado")
    print("      El ejercicio usara SQLite en su lugar")
    print("      Para instalar: pip install mysql-connector-python\n")

import pandas as pd
import os
import sys
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACION: Guardar archivos en la carpeta del script
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("="*80)
print("EJERCICIO 1 - CLASE 12: FUNCIONES SQL AVANZADAS")
print("Carlos Pulido Rosas - MCD - CUCEA")
print("="*80)
print(f"\nDirectorio del script: {SCRIPT_DIR}")
print(f"Directorio de trabajo: {os.getcwd()}")
print(f"MySQL disponible: {'SI ✓' if MYSQL_DISPONIBLE else 'NO (usando SQLite)'}\n")

def crear_separador(titulo):
    """Crea un separador visual"""
    print("\n" + "="*80)
    print(titulo.center(80))
    print("="*80)

def ejecutar_consulta(cursor, consulta, descripcion):
    """Ejecuta una consulta y muestra los resultados"""
    print(f"\n{descripcion}")
    print("-" * 80)
    print(f"SQL: {consulta}\n")
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    
    if resultados:
        for row in resultados:
            print(f"  {row}")
    else:
        print("  (Sin resultados)")
    
    return resultados

# ============================================================
# INFORMACION SOBRE EL DRIVER MYSQL
# ============================================================

crear_separador("INFORMACION DEL DRIVER MYSQL")

print("""
DRIVER PARA MYSQL: mysql-connector-python
==========================================

1. ¿QUE ES?
   - Driver oficial de Oracle para conectar Python con MySQL
   - Escrito en Python puro (no requiere compilacion)
   - Compatible con Python 3.x

2. INSTALACION:
   
   Opcion 1 - pip:
   ---------------
   pip install mysql-connector-python
   
   Opcion 2 - conda:
   -----------------
   conda install -c conda-forge mysql-connector-python

3. ALTERNATIVAS:
   - PyMySQL: Driver Python puro, ligero
   - mysqlclient: Driver en C, mas rapido pero requiere compilacion
   - SQLAlchemy: ORM que soporta multiples bases de datos

4. SINTAXIS BASICA:
   
   import mysql.connector
   
   conexion = mysql.connector.connect(
       host="localhost",
       user="usuario",
       password="contraseña",
       database="nombre_bd"
   )
   
   cursor = conexion.cursor()
   cursor.execute("SELECT * FROM tabla")
   resultados = cursor.fetchall()
   
   cursor.close()
   conexion.close()

5. VENTAJAS:
   - Oficial y bien mantenido
   - Documentacion completa
   - Soporte para parametros y transacciones
   - Compatible con MySQL 5.5+

NOTA: En este ejercicio usaremos SQLite (de la Clase 11) porque es mas
      portable y no requiere servidor MySQL instalado. Las funciones SQL
      son las mismas en ambos sistemas.
""")

# ============================================================
# PARTE 1: CONECTAR A LA BASE DE DATOS
# ============================================================

crear_separador("PARTE 1: CONEXION A LA BASE DE DATOS")

print("\n[1.1] Verificando base de datos DB_Propia.db de la Clase 11...")

if not os.path.exists('DB_Propia.db'):
    print("   ERROR: DB_Propia.db no encontrada")
    print("   Por favor, ejecuta primero el ejercicio de la Clase 11")
    sys.exit(1)

print("   Base de datos encontrada ✓")

print("\n[1.2] Conectando a la base de datos...")
conexion = sqlite3.connect('DB_Propia.db')
cursor = conexion.cursor()
print("   Conexion exitosa ✓")

# Verificar tablas
print("\n[1.3] Verificando tablas disponibles...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tablas = cursor.fetchall()
print(f"   Tablas encontradas: {len(tablas)}")
for tabla in tablas:
    print(f"   - {tabla[0]}")

# ============================================================
# PARTE 2: FUNCIONES DE AGREGACION - TABLA ESTUDIANTES
# ============================================================

crear_separador("PARTE 2: FUNCIONES DE AGREGACION - TABLA ESTUDIANTES")

print("\n>>> TABLA: Estudiantes")
print(">>> CAMPOS: id_estudiante, nombre, apellido, edad, calificacion, carrera, semestre, ciudad\n")

# 1. COUNT - Contar registros
ejecutar_consulta(
    cursor,
    "SELECT COUNT(*) as total_estudiantes FROM Estudiantes",
    "1. COUNT() - Total de estudiantes"
)

# 2. AVG - Promedio de calificaciones
ejecutar_consulta(
    cursor,
    "SELECT AVG(calificacion) as promedio_calificaciones FROM Estudiantes",
    "2. AVG() - Promedio de calificaciones"
)

# 3. MIN y MAX - Calificacion minima y maxima
ejecutar_consulta(
    cursor,
    "SELECT MIN(calificacion) as min_calif, MAX(calificacion) as max_calif FROM Estudiantes",
    "3. MIN() y MAX() - Calificacion minima y maxima"
)

# 4. SUM - Suma de edades
ejecutar_consulta(
    cursor,
    "SELECT SUM(edad) as suma_edades FROM Estudiantes",
    "4. SUM() - Suma de todas las edades"
)

# 5. GROUP BY - Estudiantes por ciudad
ejecutar_consulta(
    cursor,
    "SELECT ciudad, COUNT(*) as total FROM Estudiantes GROUP BY ciudad ORDER BY total DESC",
    "5. GROUP BY - Estudiantes por ciudad"
)

# 6. GROUP BY con AVG - Promedio de calificacion por ciudad
ejecutar_consulta(
    cursor,
    "SELECT ciudad, AVG(calificacion) as promedio FROM Estudiantes GROUP BY ciudad ORDER BY promedio DESC",
    "6. GROUP BY con AVG() - Promedio de calificacion por ciudad"
)

# 7. HAVING - Ciudades con mas de 1 estudiante
ejecutar_consulta(
    cursor,
    "SELECT ciudad, COUNT(*) as total FROM Estudiantes GROUP BY ciudad HAVING total > 1",
    "7. HAVING - Ciudades con mas de 1 estudiante"
)

# 8. ORDER BY y LIMIT - Top 5 mejores calificaciones
ejecutar_consulta(
    cursor,
    "SELECT nombre, apellido, calificacion FROM Estudiantes ORDER BY calificacion DESC LIMIT 5",
    "8. ORDER BY y LIMIT - Top 5 estudiantes con mejores calificaciones"
)

# 9. Estudiantes por semestre
ejecutar_consulta(
    cursor,
    "SELECT semestre, COUNT(*) as total, AVG(calificacion) as promedio FROM Estudiantes GROUP BY semestre ORDER BY semestre",
    "9. GROUP BY - Estudiantes por semestre con promedio"
)

# 10. Estudiantes mayores de 20 años
ejecutar_consulta(
    cursor,
    "SELECT COUNT(*) as total FROM Estudiantes WHERE edad > 20",
    "10. COUNT con WHERE - Estudiantes mayores de 20 años"
)

# ============================================================
# PARTE 3: FUNCIONES DE AGREGACION - TABLA PRODUCTOS
# ============================================================

crear_separador("PARTE 3: FUNCIONES DE AGREGACION - TABLA PRODUCTOS")

print("\n>>> TABLA: Productos")
print(">>> CAMPOS: id_producto, nombre, categoria, precio, stock, marca, proveedor, codigo\n")

# 1. COUNT - Total de productos
ejecutar_consulta(
    cursor,
    "SELECT COUNT(*) as total_productos FROM Productos",
    "1. COUNT() - Total de productos"
)

# 2. SUM - Valor total del inventario
ejecutar_consulta(
    cursor,
    "SELECT SUM(precio * stock) as valor_inventario FROM Productos",
    "2. SUM() con multiplicacion - Valor total del inventario"
)

# 3. AVG - Precio promedio
ejecutar_consulta(
    cursor,
    "SELECT AVG(precio) as precio_promedio FROM Productos",
    "3. AVG() - Precio promedio de productos"
)

# 4. MIN y MAX - Precio minimo y maximo
ejecutar_consulta(
    cursor,
    "SELECT MIN(precio) as precio_min, MAX(precio) as precio_max FROM Productos",
    "4. MIN() y MAX() - Rango de precios"
)

# 5. GROUP BY - Productos por categoria
ejecutar_consulta(
    cursor,
    "SELECT categoria, COUNT(*) as total, AVG(precio) as precio_promedio FROM Productos GROUP BY categoria ORDER BY total DESC",
    "5. GROUP BY - Productos por categoria con precio promedio"
)

# 6. GROUP BY - Productos por marca
ejecutar_consulta(
    cursor,
    "SELECT marca, COUNT(*) as total FROM Productos GROUP BY marca ORDER BY total DESC",
    "6. GROUP BY - Productos por marca"
)

# 7. HAVING - Categorias con precio promedio mayor a 2000
ejecutar_consulta(
    cursor,
    "SELECT categoria, AVG(precio) as promedio FROM Productos GROUP BY categoria HAVING promedio > 2000",
    "7. HAVING - Categorias con precio promedio mayor a 2000"
)

# 8. ORDER BY y LIMIT - Top 3 productos mas caros
ejecutar_consulta(
    cursor,
    "SELECT nombre, precio, categoria FROM Productos ORDER BY precio DESC LIMIT 3",
    "8. ORDER BY y LIMIT - Top 3 productos mas caros"
)

# 9. Stock total por categoria
ejecutar_consulta(
    cursor,
    "SELECT categoria, SUM(stock) as stock_total FROM Productos GROUP BY categoria ORDER BY stock_total DESC",
    "9. SUM() con GROUP BY - Stock total por categoria"
)

# 10. Productos con stock bajo (menos de 50)
ejecutar_consulta(
    cursor,
    "SELECT COUNT(*) as productos_bajo_stock FROM Productos WHERE stock < 50",
    "10. COUNT con WHERE - Productos con stock bajo (< 50)"
)

# ============================================================
# PARTE 4: FUNCIONES DE AGREGACION - TABLA EMPLEADOS
# ============================================================

crear_separador("PARTE 4: FUNCIONES DE AGREGACION - TABLA EMPLEADOS")

print("\n>>> TABLA: Empleados")
print(">>> CAMPOS: id_empleado, nombre, apellido, puesto, salario, departamento, antiguedad, email\n")

# 1. COUNT - Total de empleados
ejecutar_consulta(
    cursor,
    "SELECT COUNT(*) as total_empleados FROM Empleados",
    "1. COUNT() - Total de empleados"
)

# 2. SUM - Nomina total
ejecutar_consulta(
    cursor,
    "SELECT SUM(salario) as nomina_total FROM Empleados",
    "2. SUM() - Nomina total mensual"
)

# 3. AVG - Salario promedio
ejecutar_consulta(
    cursor,
    "SELECT AVG(salario) as salario_promedio FROM Empleados",
    "3. AVG() - Salario promedio"
)

# 4. MIN y MAX - Salario minimo y maximo
ejecutar_consulta(
    cursor,
    "SELECT MIN(salario) as salario_min, MAX(salario) as salario_max FROM Empleados",
    "4. MIN() y MAX() - Rango salarial"
)

# 5. GROUP BY - Empleados por departamento
ejecutar_consulta(
    cursor,
    "SELECT departamento, COUNT(*) as total_empleados, AVG(salario) as salario_promedio FROM Empleados GROUP BY departamento ORDER BY salario_promedio DESC",
    "5. GROUP BY - Empleados por departamento con salario promedio"
)

# 6. HAVING - Departamentos con salario promedio mayor a 30000
ejecutar_consulta(
    cursor,
    "SELECT departamento, AVG(salario) as promedio FROM Empleados GROUP BY departamento HAVING promedio > 30000",
    "6. HAVING - Departamentos con salario promedio > 30000"
)

# 7. ORDER BY y LIMIT - Top 3 salarios mas altos
ejecutar_consulta(
    cursor,
    "SELECT nombre, apellido, puesto, salario FROM Empleados ORDER BY salario DESC LIMIT 3",
    "7. ORDER BY y LIMIT - Top 3 salarios mas altos"
)

# 8. Antiguedad promedio
ejecutar_consulta(
    cursor,
    "SELECT AVG(antiguedad) as antiguedad_promedio FROM Empleados",
    "8. AVG() - Antiguedad promedio en años"
)

# 9. Empleados con mas de 5 años de antiguedad
ejecutar_consulta(
    cursor,
    "SELECT COUNT(*) as empleados_antiguos FROM Empleados WHERE antiguedad > 5",
    "9. COUNT con WHERE - Empleados con mas de 5 años"
)

# 10. Nomina por departamento
ejecutar_consulta(
    cursor,
    "SELECT departamento, SUM(salario) as nomina_dept FROM Empleados GROUP BY departamento ORDER BY nomina_dept DESC",
    "10. SUM() con GROUP BY - Nomina por departamento"
)

# ============================================================
# PARTE 5: CONSULTAS AVANZADAS COMBINADAS
# ============================================================

crear_separador("PARTE 5: CONSULTAS AVANZADAS COMBINADAS")

print("\n>>> CONSULTAS QUE COMBINAN MULTIPLES FUNCIONES\n")

# 1. Estadisticas completas de estudiantes
print("\n1. Estadisticas completas de estudiantes")
print("-" * 80)
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        AVG(edad) as edad_promedio,
        MIN(edad) as edad_minima,
        MAX(edad) as edad_maxima,
        AVG(calificacion) as calificacion_promedio,
        MIN(calificacion) as calificacion_minima,
        MAX(calificacion) as calificacion_maxima
    FROM Estudiantes
""")
resultado = cursor.fetchone()
print(f"  Total estudiantes: {resultado[0]}")
print(f"  Edad promedio: {resultado[1]:.1f} años")
print(f"  Edad minima: {resultado[2]} años")
print(f"  Edad maxima: {resultado[3]} años")
print(f"  Calificacion promedio: {resultado[4]:.1f}")
print(f"  Calificacion minima: {resultado[5]}")
print(f"  Calificacion maxima: {resultado[6]}")

# 2. Estadisticas completas de productos
print("\n2. Estadisticas completas de productos")
print("-" * 80)
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(stock) as stock_total,
        AVG(precio) as precio_promedio,
        MIN(precio) as precio_minimo,
        MAX(precio) as precio_maximo,
        SUM(precio * stock) as valor_inventario
    FROM Productos
""")
resultado = cursor.fetchone()
print(f"  Total productos: {resultado[0]}")
print(f"  Stock total: {resultado[1]} unidades")
print(f"  Precio promedio: ${resultado[2]:,.2f}")
print(f"  Precio minimo: ${resultado[3]:,.2f}")
print(f"  Precio maximo: ${resultado[4]:,.2f}")
print(f"  Valor total inventario: ${resultado[5]:,.2f}")

# 3. Estadisticas completas de empleados
print("\n3. Estadisticas completas de empleados")
print("-" * 80)
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(salario) as nomina_total,
        AVG(salario) as salario_promedio,
        MIN(salario) as salario_minimo,
        MAX(salario) as salario_maximo,
        AVG(antiguedad) as antiguedad_promedio
    FROM Empleados
""")
resultado = cursor.fetchone()
print(f"  Total empleados: {resultado[0]}")
print(f"  Nomina total: ${resultado[1]:,.2f}")
print(f"  Salario promedio: ${resultado[2]:,.2f}")
print(f"  Salario minimo: ${resultado[3]:,.2f}")
print(f"  Salario maximo: ${resultado[4]:,.2f}")
print(f"  Antiguedad promedio: {resultado[5]:.1f} años")

# ============================================================
# PARTE 6: EXPORTAR RESULTADOS A CSV
# ============================================================

crear_separador("PARTE 6: EXPORTAR RESULTADOS A CSV")

print("\n[6.1] Generando reportes en CSV...")

# Reporte 1: Estudiantes por ciudad
cursor.execute("""
    SELECT ciudad, COUNT(*) as total, AVG(calificacion) as promedio
    FROM Estudiantes 
    GROUP BY ciudad 
    ORDER BY total DESC
""")
df1 = pd.DataFrame(cursor.fetchall(), columns=['Ciudad', 'Total_Estudiantes', 'Calificacion_Promedio'])
df1.to_csv('reporte_estudiantes_por_ciudad.csv', index=False, encoding='utf-8')
print("   ✓ reporte_estudiantes_por_ciudad.csv")

# Reporte 2: Productos por categoria
cursor.execute("""
    SELECT categoria, COUNT(*) as total, AVG(precio) as precio_promedio, SUM(stock) as stock_total
    FROM Productos 
    GROUP BY categoria 
    ORDER BY total DESC
""")
df2 = pd.DataFrame(cursor.fetchall(), columns=['Categoria', 'Total_Productos', 'Precio_Promedio', 'Stock_Total'])
df2.to_csv('reporte_productos_por_categoria.csv', index=False, encoding='utf-8')
print("   ✓ reporte_productos_por_categoria.csv")

# Reporte 3: Empleados por departamento
cursor.execute("""
    SELECT departamento, COUNT(*) as total, AVG(salario) as salario_promedio, SUM(salario) as nomina
    FROM Empleados 
    GROUP BY departamento 
    ORDER BY nomina DESC
""")
df3 = pd.DataFrame(cursor.fetchall(), columns=['Departamento', 'Total_Empleados', 'Salario_Promedio', 'Nomina_Total'])
df3.to_csv('reporte_empleados_por_departamento.csv', index=False, encoding='utf-8')
print("   ✓ reporte_empleados_por_departamento.csv")

print(f"\n   Archivos CSV guardados en: {SCRIPT_DIR}")

# ============================================================
# RESUMEN FINAL
# ============================================================

crear_separador("RESUMEN DE FUNCIONES SQL APLICADAS")

print("""
FUNCIONES SQL APLICADAS:
========================

1. COUNT()      - Contar registros
2. SUM()        - Sumar valores numericos
3. AVG()        - Calcular promedio
4. MIN()        - Obtener valor minimo
5. MAX()        - Obtener valor maximo
6. GROUP BY     - Agrupar datos por columna
7. HAVING       - Filtrar grupos (como WHERE pero para grupos)
8. ORDER BY     - Ordenar resultados (ASC/DESC)
9. LIMIT        - Limitar numero de resultados
10. WHERE       - Filtrar registros individuales

COMBINACIONES APLICADAS:
========================

- COUNT() + GROUP BY
- AVG() + GROUP BY
- SUM() + GROUP BY
- MIN() y MAX() en una sola consulta
- GROUP BY + HAVING + ORDER BY
- Multiples funciones de agregacion en una consulta
- WHERE + COUNT()
- ORDER BY + LIMIT (Top N)

TABLAS ANALIZADAS:
==================

1. Estudiantes  - 10 registros
2. Productos    - 10 registros
3. Empleados    - 10 registros

TOTAL: 30 consultas SQL ejecutadas
""")

# Cerrar conexion
cursor.close()
conexion.close()

crear_separador("EJERCICIO COMPLETADO")

print("\nArchivos generados en:")
print(f"  {SCRIPT_DIR}\n")

archivos_generados = [
    'reporte_estudiantes_por_ciudad.csv',
    'reporte_productos_por_categoria.csv',
    'reporte_empleados_por_departamento.csv'
]

print("Archivos CSV generados:")
for archivo in archivos_generados:
    ruta = os.path.join(SCRIPT_DIR, archivo)
    existe = os.path.exists(archivo)
    simbolo = '[✓]' if existe else '[✗]'
    print(f"  {simbolo} {archivo}")
    if existe:
        print(f"      {ruta}")

print("\nFunciones SQL aplicadas: 10/10 ✓")
print("Consultas ejecutadas: 30+ ✓")
print("Reportes generados: 3 ✓")

print("\n" + "="*80)
print("DRIVER MYSQL RECOMENDADO: mysql-connector-python")
print("Instalacion: pip install mysql-connector-python")
print("="*80 + "\n")