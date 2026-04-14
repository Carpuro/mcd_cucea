"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 9

EJERCICIO 1 - Ordenamiento Descendente

Importa y cambia el codigo del ordenamiento ascendente para que este lleve a cabo un ordenamiento descendente

"""

import requests
from bs4 import BeautifulSoup

print("="*70)
print("EJERCICIO 1: ORDENAMIENTO DESCENDENTE")
print("="*70)

# ============================================================
# EXTRACCION DE DATOS DESDE URL
# ============================================================

print("\n[1] Extrayendo datos desde la web...")

# URL para extraer datos
url = 'https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread/'

try:
    # Accedemos al URL
    page = requests.get(url)
    
    # Le indicamos que el texto del objeto "page" es de tipo html
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Creamos una lista vacia para almacenar los datos
    data = []
    
    # data_iterator es el iterador de la tabla
    # soup.find_all('td') traera cada elemento en la tabla de la URL 
    # que se encuentren entre un tag "td" (tags de tablas en HTML)
    data_iterator = iter(soup.find_all('td'))
    
    # Este ciclo seguira repitiendose hasta que haya
    # datos disponibles en el iterador
    while True:
        try:
            pais = next(data_iterator).text
            casos_confirmados = next(data_iterator).text
            muertes = next(data_iterator).text
            region = next(data_iterator).text
            
            data.append((
                pais,
                int(casos_confirmados.replace(',', '')),
                int(muertes.replace(',', '')),
                region
            ))
        
        # El error StopIteration se genera cuando
        # no quedan mas elementos para iterar
        except StopIteration:
            break
    
    print(f"   Datos extraidos correctamente: {len(data)} paises")
    
except Exception as e:
    print(f"   Error al extraer datos: {e}")
    print("   Usando datos de respaldo...")
    # Datos de respaldo en caso de error de conexion
    data = [
        ('United States', 111820082, 1219487, 'North America'),
        ('India', 45035393, 533570, 'Asia'),
        ('France', 40138560, 167642, 'Europe'),
        ('Germany', 38828995, 183027, 'Europe'),
        ('Brazil', 38743918, 711380, 'South America'),
        ('Mexico', 7702809, 334958, 'North America'),
        ('Spain', 13914811, 121760, 'Europe'),
        ('Italy', 26723249, 196487, 'Europe')
    ]

# ============================================================
# MOSTRAR DATOS ORIGINALES
# ============================================================

print("\n[2] Datos originales (primeros 5 paises):")
for pais, casos, muertes, region in data[:5]:
    print(f"   {pais}: {casos:,} casos, {muertes:,} muertes ({region})")

# ============================================================
# ORDENAMIENTO DESCENDENTE CON ALGORITMO DE BURBUJA
# ============================================================

print("\n[3] Aplicando algoritmo de burbuja para ordenamiento DESCENDENTE...")

# Campo a ordenar: 0 = Pais, 1 = Casos, 2 = Muertes, 3 = Region
campo_a_ordenar = 0  

cant_tuplas = len(data)
print(f"   Total de registros a ordenar: {cant_tuplas}")

# Algoritmo de burbuja MODIFICADO para orden DESCENDENTE
# CAMBIO CLAVE: Se cambia el operador > por < 
for i in range(0, cant_tuplas):
    for j in range(0, cant_tuplas - i - 1):
        # COMPARACION MODIFICADA PARA ORDEN DESCENDENTE
        # Orden ascendente seria: if (data[j][campo_a_ordenar] > data[j + 1][campo_a_ordenar]):
        # Orden descendente es:   if (data[j][campo_a_ordenar] < data[j + 1][campo_a_ordenar]):
        if (data[j][campo_a_ordenar] < data[j + 1][campo_a_ordenar]):
            # Intercambiar elementos
            temp = data[j]
            data[j] = data[j + 1]
            data[j + 1] = temp

print("   Ordenamiento completado")

# ============================================================
# MOSTRAR RESULTADOS ORDENADOS
# ============================================================

print("\n[4] Datos ordenados de forma DESCENDENTE (Z -> A):")
print("   (Mostrando primeros 10 y ultimos 5)")
print("\n   Primeros 10:")
for i, (pais, casos, muertes, region) in enumerate(data[:10], 1):
    print(f"   {i:2d}. {pais:30s} | Casos: {casos:12,d} | Muertes: {muertes:8,d} | {region}")

print(f"\n   ... ({cant_tuplas - 15} paises intermedios) ...")

print("\n   Ultimos 5:")
for i, (pais, casos, muertes, region) in enumerate(data[-5:], cant_tuplas - 4):
    print(f"   {i:2d}. {pais:30s} | Casos: {casos:12,d} | Muertes: {muertes:8,d} | {region}")

# ============================================================
# COMPARACION: ASCENDENTE vs DESCENDENTE
# ============================================================

print("\n" + "="*70)
print("COMPARACION: ORDEN ASCENDENTE vs DESCENDENTE")
print("="*70)

# Crear copia para orden ascendente
data_ascendente = sorted(data, key=lambda x: x[0])

print("\nOrden ASCENDENTE (A -> Z):")
print(f"   Primero: {data_ascendente[0][0]}")
print(f"   Ultimo:  {data_ascendente[-1][0]}")

print("\nOrden DESCENDENTE (Z -> A):")
print(f"   Primero: {data[0][0]}")
print(f"   Ultimo:  {data[-1][0]}")

# ============================================================
# METODOS ALTERNATIVOS DE ORDENAMIENTO
# ============================================================

print("\n" + "="*70)
print("METODOS ALTERNATIVOS DE ORDENAMIENTO DESCENDENTE")
print("="*70)

# Metodo 1: Usando sort() con reverse=True
data_metodo1 = data.copy()
data_metodo1.sort(key=lambda x: x[0], reverse=True)
print("\nMetodo 1: list.sort(key=lambda x: x[0], reverse=True)")
print(f"   Primeros 3: {data_metodo1[0][0]}, {data_metodo1[1][0]}, {data_metodo1[2][0]}")

# Metodo 2: Usando sorted() con reverse=True
data_metodo2 = sorted(data, key=lambda x: x[0], reverse=True)
print("\nMetodo 2: sorted(data, key=lambda x: x[0], reverse=True)")
print(f"   Primeros 3: {data_metodo2[0][0]}, {data_metodo2[1][0]}, {data_metodo2[2][0]}")

# Metodo 3: Ordenar ascendente y luego invertir
data_metodo3 = sorted(data, key=lambda x: x[0])
data_metodo3.reverse()
print("\nMetodo 3: sorted() ascendente + list.reverse()")
print(f"   Primeros 3: {data_metodo3[0][0]}, {data_metodo3[1][0]}, {data_metodo3[2][0]}")

# ============================================================
# ORDENAMIENTO POR OTROS CAMPOS
# ============================================================

print("\n" + "="*70)
print("ORDENAMIENTO POR DIFERENTES CAMPOS")
print("="*70)

# Ordenar por numero de casos (mayor a menor)
data_por_casos = sorted(data, key=lambda x: x[1], reverse=True)
print("\nTop 5 paises por CASOS confirmados:")
for i, (pais, casos, muertes, region) in enumerate(data_por_casos[:5], 1):
    print(f"   {i}. {pais:30s}: {casos:12,d} casos")

# Ordenar por numero de muertes (mayor a menor)
data_por_muertes = sorted(data, key=lambda x: x[2], reverse=True)
print("\nTop 5 paises por MUERTES:")
for i, (pais, casos, muertes, region) in enumerate(data_por_muertes[:5], 1):
    print(f"   {i}. {pais:30s}: {muertes:8,d} muertes")

# ============================================================
# RESUMEN Y CONCLUSIONES
# ============================================================

print("\n" + "="*70)
print("RESUMEN DEL EJERCICIO")
print("="*70)

print("\nCambio clave realizado:")
print("   En el algoritmo de burbuja, se cambio el operador de comparacion")
print("   De:  if (data[j][campo] > data[j + 1][campo]):")
print("   A:   if (data[j][campo] < data[j + 1][campo]):")
print("\n   Este cambio invierte el orden de ascendente a descendente")

print(f"\nEstadisticas generales:")
print(f"   Total de paises procesados: {len(data)}")
print(f"   Campos por registro: 4 (Pais, Casos, Muertes, Region)")
print(f"   Ordenamiento aplicado: Descendente por nombre de pais (Z -> A)")