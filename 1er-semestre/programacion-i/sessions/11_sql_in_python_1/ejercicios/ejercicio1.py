"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 11

EJERCICIO 1 - SQL EN PYTHON 1

    PARTE 1: Crear DB_Propia con 3 tablas.
    PARTE 2: Graficos del Maraton NY con datos REALES del CSV.
    PARTE 3: Crear un histograma y un grafico de barras con los datos de Maraton NY previamente importados a una BD.

"""

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
import os
import sys

# Ignorar warnings de pandas y numpy
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURACION: Guardar archivos en la carpeta del script
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

print("="*70)
print("EJERCICIO 1 - SQL EN PYTHON")
print("Carlos Pulido Rosas - MCD - CUCEA")
print("="*70)
print(f"\nDirectorio del script: {SCRIPT_DIR}")
print(f"Directorio de trabajo: {os.getcwd()}\n")

def crear_separador(titulo):
    """Crea un separador visual"""
    print("\n" + "="*70)
    print(titulo.center(70))
    print("="*70)

# ============================================================
# PARTE 1: BASE DE DATOS PROPIA
# ============================================================

crear_separador("PARTE 1: CREACION DE BASE DE DATOS PROPIA")

print("\n[1.1] Creando base de datos DB_Propia.db...")

if os.path.exists('DB_Propia.db'):
    os.remove('DB_Propia.db')

conexion1 = sqlite3.connect('DB_Propia.db')
cursor1 = conexion1.cursor()

# Tabla 1: Estudiantes
print("\n[1.2] Creando tabla Estudiantes...")
cursor1.execute('''
    CREATE TABLE Estudiantes (
        id_estudiante INTEGER PRIMARY KEY,
        nombre VARCHAR(50),
        apellido VARCHAR(50),
        edad INTEGER,
        calificacion INTEGER,
        carrera VARCHAR(100),
        semestre INTEGER,
        ciudad VARCHAR(50)
    )
''')

estudiantes = [
    (1, 'Juan', 'Perez', 20, 85, 'Ingenieria en Sistemas', 4, 'Guadalajara'),
    (2, 'Maria', 'Lopez', 22, 92, 'Administracion', 6, 'Monterrey'),
    (3, 'Carlos', 'Garcia', 21, 78, 'Derecho', 5, 'Ciudad de Mexico'),
    (4, 'Ana', 'Martinez', 19, 88, 'Medicina', 3, 'Puebla'),
    (5, 'Luis', 'Rodriguez', 23, 95, 'Ingenieria Civil', 7, 'Tijuana'),
    (6, 'Sofia', 'Hernandez', 20, 82, 'Psicologia', 4, 'Queretaro'),
    (7, 'Diego', 'Gonzalez', 22, 90, 'Arquitectura', 6, 'Leon'),
    (8, 'Valentina', 'Ramirez', 21, 87, 'Contaduria', 5, 'Merida'),
    (9, 'Miguel', 'Torres', 19, 76, 'Comunicacion', 3, 'Cancun'),
    (10, 'Isabella', 'Flores', 24, 93, 'Derecho', 8, 'Guadalajara')
]
cursor1.executemany('INSERT INTO Estudiantes VALUES (?, ?, ?, ?, ?, ?, ?, ?)', estudiantes)
print("    Tabla Estudiantes: 10 registros insertados")

# Tabla 2: Productos
print("\n[1.3] Creando tabla Productos...")
cursor1.execute('''
    CREATE TABLE Productos (
        id_producto INTEGER PRIMARY KEY,
        nombre VARCHAR(100),
        categoria VARCHAR(50),
        precio INTEGER,
        stock INTEGER,
        marca VARCHAR(50),
        proveedor VARCHAR(100),
        codigo VARCHAR(20)
    )
''')

productos = [
    (1, 'Laptop HP', 'Electronica', 15000, 25, 'HP', 'TechSupply', 'LP-HP-001'),
    (2, 'Mouse Logitech', 'Accesorios', 800, 150, 'Logitech', 'CompuMex', 'MS-LG-002'),
    (3, 'Teclado Mecanico', 'Accesorios', 1200, 80, 'Razer', 'GamerStore', 'KB-RZ-003'),
    (4, 'Monitor Samsung', 'Electronica', 5500, 40, 'Samsung', 'DisplayPro', 'MN-SS-004'),
    (5, 'Impresora Canon', 'Oficina', 3200, 30, 'Canon', 'OfficeMart', 'PR-CN-005'),
    (6, 'Disco Duro 1TB', 'Almacenamiento', 1500, 200, 'Western Digital', 'DataStore', 'HD-WD-006'),
    (7, 'Memoria RAM 16GB', 'Componentes', 2800, 120, 'Kingston', 'TechSupply', 'RM-KS-007'),
    (8, 'Webcam Logitech', 'Accesorios', 1800, 60, 'Logitech', 'CompuMex', 'WC-LG-008'),
    (9, 'Router TP-Link', 'Redes', 950, 90, 'TP-Link', 'NetWorld', 'RT-TP-009'),
    (10, 'Audifonos Sony', 'Audio', 2200, 100, 'Sony', 'SoundHub', 'AU-SN-010')
]
cursor1.executemany('INSERT INTO Productos VALUES (?, ?, ?, ?, ?, ?, ?, ?)', productos)
print("    Tabla Productos: 10 registros insertados")

# Tabla 3: Empleados
print("\n[1.4] Creando tabla Empleados...")
cursor1.execute('''
    CREATE TABLE Empleados (
        id_empleado INTEGER PRIMARY KEY,
        nombre VARCHAR(50),
        apellido VARCHAR(50),
        puesto VARCHAR(50),
        salario INTEGER,
        departamento VARCHAR(50),
        antiguedad INTEGER,
        email VARCHAR(100)
    )
''')

empleados = [
    (1, 'Roberto', 'Sanchez', 'Gerente General', 45000, 'Administracion', 8, 'roberto@empresa.com'),
    (2, 'Laura', 'Mendoza', 'Desarrolladora Senior', 35000, 'Tecnologia', 5, 'laura@empresa.com'),
    (3, 'Fernando', 'Cruz', 'Analista de Datos', 28000, 'Tecnologia', 3, 'fernando@empresa.com'),
    (4, 'Patricia', 'Morales', 'Coordinadora RH', 32000, 'Recursos Humanos', 6, 'patricia@empresa.com'),
    (5, 'Alejandro', 'Vargas', 'Contador', 30000, 'Finanzas', 4, 'alejandro@empresa.com'),
    (6, 'Gabriela', 'Ruiz', 'Disenadora', 25000, 'Marketing', 2, 'gabriela@empresa.com'),
    (7, 'Ricardo', 'Ortiz', 'Vendedor', 22000, 'Ventas', 3, 'ricardo@empresa.com'),
    (8, 'Monica', 'Castro', 'Asistente', 20000, 'Administracion', 5, 'monica@empresa.com'),
    (9, 'Jorge', 'Jimenez', 'Supervisor', 33000, 'Operaciones', 7, 'jorge@empresa.com'),
    (10, 'Carmen', 'Reyes', 'Jefa Marketing', 38000, 'Marketing', 6, 'carmen@empresa.com')
]
cursor1.executemany('INSERT INTO Empleados VALUES (?, ?, ?, ?, ?, ?, ?, ?)', empleados)
print("    Tabla Empleados: 10 registros insertados")

conexion1.commit()
print("\n[1.5] Base de datos DB_Propia.db creada exitosamente")
print(f"      Ubicacion: {os.path.join(SCRIPT_DIR, 'DB_Propia.db')}")
print("      Total: 3 tablas, 30 registros")

# ============================================================
# PARTE 2: MARATON NY CON DATOS REALES
# ============================================================

crear_separador("PARTE 2: MARATON NY - DATOS REALES DEL CSV")

print("\n[2.1] Verificando archivo MaratonNY.csv...")

if not os.path.exists('MaratonNY.csv'):
    print("   ERROR: Archivo MaratonNY.csv no encontrado")
    print(f"   Asegurese de que el archivo este en: {SCRIPT_DIR}")
else:
    # Leer CSV
    print("\n[2.2] Leyendo datos desde MaratonNY.csv...")
    df = pd.read_csv('MaratonNY.csv')
    print(f"   Archivo leido: {len(df)} registros")
    
    # Crear base de datos
    print("\n[2.3] Creando base de datos Maraton_NY.db...")
    if os.path.exists('Maraton_NY.db'):
        os.remove('Maraton_NY.db')
    
    conexion2 = sqlite3.connect('Maraton_NY.db')
    cursor2 = conexion2.cursor()
    
    # Importar datos
    print("\n[2.4] Importando datos del CSV a la base de datos...")
    df.to_sql('Resultados_Maraton', conexion2, if_exists='replace', index=False)
    print(f"   {len(df)} registros importados")
    print(f"   Ubicacion: {os.path.join(SCRIPT_DIR, 'Maraton_NY.db')}")
    
    # Extraer datos para graficos
    print("\n[2.5] Extrayendo datos para visualizacion...")
    cursor2.execute("SELECT time FROM Resultados_Maraton")
    tiempos = [row[0] for row in cursor2.fetchall()]
    
    cursor2.execute('''
        SELECT home, AVG(time) as promedio, COUNT(*) as cantidad
        FROM Resultados_Maraton
        GROUP BY home
        HAVING cantidad >= 3
        ORDER BY promedio
        LIMIT 15
    ''')
    datos_ubicacion = cursor2.fetchall()
    ubicaciones = [row[0] for row in datos_ubicacion]
    promedios = [row[1] for row in datos_ubicacion]
    
    # Estadisticas
    cursor2.execute('SELECT COUNT(*), AVG(time), MIN(time), MAX(time) FROM Resultados_Maraton')
    stats = cursor2.fetchone()
    
    print(f"   Tiempos extraidos: {len(tiempos)} registros")
    print(f"   Ubicaciones con 3+ corredores: {len(ubicaciones)}")
    print(f"   Tiempo promedio: {stats[1]:.1f} min ({stats[1]/60:.2f} hrs)")
    
    # Crear graficos
    print("\n[2.6] Generando graficos...")
    
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle('Analisis del Maraton de Nueva York (Datos Reales)', 
                fontsize=18, fontweight='bold', y=1.02)
    
    # HISTOGRAMA
    ax1 = plt.subplot(1, 2, 1)
    n, bins, patches = ax1.hist(tiempos, bins=20, color='#3498db', 
                                edgecolor='black', alpha=0.75, linewidth=1.2)
    ax1.set_xlabel('Tiempo (minutos)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Frecuencia', fontsize=13, fontweight='bold')
    ax1.set_title('Histograma: Distribucion de Tiempos', 
                 fontsize=14, fontweight='bold', pad=15)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    promedio = np.mean(tiempos)
    mediana = np.median(tiempos)
    ax1.axvline(promedio, color='red', linestyle='--', linewidth=2.5, 
               label=f'Promedio: {promedio:.1f} min')
    ax1.axvline(mediana, color='green', linestyle='--', linewidth=2.5,
               label=f'Mediana: {mediana:.1f} min')
    ax1.legend(loc='upper right', fontsize=11)
    
    stats_text = f'N = {len(tiempos)}\nMedia: {promedio:.1f} min\n'
    stats_text += f'Mediana: {mediana:.1f} min\nDesv: {np.std(tiempos):.1f} min'
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            fontsize=10, family='monospace')
    
    # GRAFICO DE BARRAS
    ax2 = plt.subplot(1, 2, 2)
    x_pos = np.arange(len(ubicaciones))
    colores = plt.cm.viridis(np.linspace(0.2, 0.9, len(ubicaciones)))
    barras = ax2.bar(x_pos, promedios, color=colores, 
                    edgecolor='black', alpha=0.85, linewidth=1.2)
    
    ax2.set_xlabel('Ubicacion', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Tiempo Promedio (min)', fontsize=13, fontweight='bold')
    ax2.set_title('Grafico de Barras: Tiempo por Ubicacion',
                 fontsize=14, fontweight='bold', pad=15)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(ubicaciones, rotation=45, ha='right', fontsize=10)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    for barra, valor in zip(barras, promedios):
        altura = barra.get_height()
        ax2.text(barra.get_x() + barra.get_width()/2., altura,
                f'{valor:.1f}', ha='center', va='bottom', 
                fontsize=9, fontweight='bold')
    
    ax2.axhline(promedio, color='red', linestyle='--', linewidth=2,
               alpha=0.7, label=f'Promedio general: {promedio:.1f} min')
    ax2.legend(loc='upper left', fontsize=10)
    
    plt.tight_layout()
    ruta_imagen = os.path.join(SCRIPT_DIR, 'graficos_maraton_ny.png')
    plt.savefig('graficos_maraton_ny.png', dpi=300, bbox_inches='tight')
    print(f"    Graficos guardados en: {ruta_imagen}")
    plt.show()
    
    # Estadisticas adicionales
    print("\n[2.7] Estadisticas del maraton:")
    print(f"    Total corredores: {stats[0]}")
    print(f"    Tiempo promedio: {stats[1]:.1f} min ({stats[1]/60:.2f} hrs)")
    print(f"    Tiempo minimo: {stats[2]:.1f} min")
    print(f"    Tiempo maximo: {stats[3]:.1f} min")
    
    cursor2.execute('''
        SELECT gender, COUNT(*), AVG(time) 
        FROM Resultados_Maraton GROUP BY gender
    ''')
    print("\n    Por genero:")
    for row in cursor2.fetchall():
        print(f"      {row[0]}: {row[1]} corredores | Promedio: {row[2]:.1f} min")
    
    conexion2.close()

# Cerrar conexion
conexion1.close()

# Resumen final
crear_separador("EJERCICIO COMPLETADO")
print("\nUbicacion de todos los archivos:")
print(f"  {SCRIPT_DIR}\n")

print("Archivos generados:")
archivos = [
    ('DB_Propia.db', 'Base de datos propia (3 tablas, 30 registros)'),
    ('Maraton_NY.db', 'Base de datos del maraton (datos reales del CSV)'),
    ('graficos_maraton_ny.png', 'Histograma y grafico de barras')
]

for archivo, descripcion in archivos:
    ruta_completa = os.path.join(SCRIPT_DIR, archivo)
    existe = os.path.exists(archivo)
    simbolo = '[✓]' if existe else '[✗]'
    print(f"  {simbolo} {archivo}")
    print(f"      {descripcion}")
    if existe:
        print(f"      {ruta_completa}")
    print()

print("Datos utilizados:")
print("  - Parte 1: Datos creados manualmente")
print("  - Parte 2: MaratonNY.csv (datos reales)")

print("\nDirectrices cumplidas:")
print("  [X] BD con 3 tablas (INT y VARCHAR)")
print("  [X] 10 registros minimo por tabla")
print("  [X] Datos del maraton importados desde CSV")
print("  [X] Histograma de tiempos del maraton")
print("  [X] Grafico de barras del maraton")
print("\n" + "="*70 + "\n")