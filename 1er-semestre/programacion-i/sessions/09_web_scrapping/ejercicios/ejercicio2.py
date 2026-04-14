"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 9

EJERCICIO 2 - Números Repetidos con count()
Crea una lista que contenga los números repetidos en el objeto "num" utilizando count()
"""

# Lista de ejemplo
num = [4, 7, 8, 9, 2, 4, 2, 9]

print("="*70)
print("EJERCICIO 2: ENCONTRAR NÚMEROS REPETIDOS CON count()")
print("="*70)

print(f"\nLista original: {num}")

# ============================================================
# SOLUCIÓN: Usando count() para encontrar repetidos
# ============================================================

num_rep = []

print("\nBuscando números repetidos...")

for numero in num:
    # Si el número aparece más de 1 vez Y no está ya en la lista de repetidos
    if num.count(numero) > 1 and numero not in num_rep:
        num_rep.append(numero)
        print(f"   ✓ {numero} aparece {num.count(numero)} veces - REPETIDO")
    elif num.count(numero) == 1:
        print(f"   • {numero} aparece 1 vez - único")

print(f"\nNúmeros repetidos encontrados: {num_rep}")

# ============================================================
# ANÁLISIS DETALLADO
# ============================================================

print("\n" + "="*70)
print("ANÁLISIS DETALLADO DE FRECUENCIAS")
print("="*70)

# Crear un diccionario con las frecuencias
frecuencias = {}
for numero in set(num):  # set() elimina duplicados
    frecuencias[numero] = num.count(numero)

print("\nFrecuencia de cada número:")
for numero, cantidad in sorted(frecuencias.items()):
    estado = "REPETIDO" if cantidad > 1 else "único"
    print(f"   {numero}: aparece {cantidad} vez/veces - {estado}")

# ============================================================
# SOLUCIONES ALTERNATIVAS
# ============================================================

print("\n" + "="*70)
print("MÉTODOS ALTERNATIVOS")
print("="*70)

# Método 1: List comprehension con count()
num_rep_v2 = [n for n in set(num) if num.count(n) > 1]
print(f"\nMétodo 1 - List comprehension:")
print(f"   {sorted(num_rep_v2)}")

# Método 2: Usando un diccionario para contar
from collections import Counter
contador = Counter(num)
num_rep_v3 = [n for n, count in contador.items() if count > 1]
print(f"\nMétodo 2 - Counter de collections:")
print(f"   {sorted(num_rep_v3)}")

# Método 3: Ciclos anidados (como en el ejemplo de clase)
num_rep_v4 = []
for i in range(len(num)):
    for j in range(len(num)):
        if i != j:
            if num[i] == num[j] and num[i] not in num_rep_v4:
                num_rep_v4.append(num[i])
print(f"\nMétodo 3 - Ciclos anidados:")
print(f"   {sorted(num_rep_v4)}")

# Método 4: Usando set para encontrar duplicados
num_rep_v5 = list(set([n for n in num if num.count(n) > 1]))
print(f"\nMétodo 4 - Set comprehension:")
print(f"   {sorted(num_rep_v5)}")

# ============================================================
# COMPARACIÓN DE MÉTODOS
# ============================================================

print("\n" + "="*70)
print("COMPARACIÓN DE MÉTODOS")
print("="*70)

print("\nVENTAJAS Y DESVENTAJAS:")

print("\n1️⃣ Método con count() (SOLUCIÓN PEDIDA):")
print("   ✅ Usa el método count() como se pide")
print("   ✅ Fácil de entender")
print("   ❌ Menos eficiente para listas grandes (O(n²))")

print("\n2️⃣ Método con Counter:")
print("   ✅ Más eficiente (O(n))")
print("   ✅ Proporciona frecuencias directamente")
print("   ❌ Requiere importar módulo")

print("\n3️⃣ Método con ciclos anidados:")
print("   ✅ No requiere métodos especiales")
print("   ❌ Más complejo de leer")
print("   ❌ Menos eficiente (O(n²))")

print("\n4️⃣ Método con set:")
print("   ✅ Muy conciso (una línea)")
print("   ❌ Puede ser difícil de entender para principiantes")

# ============================================================
# EJEMPLO CON OTRA LISTA
# ============================================================

print("\n" + "="*70)
print("PROBANDO CON OTRA LISTA")
print("="*70)

num2 = [1, 2, 3, 4, 5, 1, 2, 6, 7, 8, 1, 9, 10]
print(f"\nLista: {num2}")

num_rep2 = [n for n in set(num2) if num2.count(n) > 1]
print(f"Repetidos: {sorted(num_rep2)}")

print("\nDetalle:")
for n in sorted(set(num2)):
    count = num2.count(n)
    if count > 1:
        print(f"   {n}: aparece {count} veces")

print("\n" + "="*70)
print("\nLa clave es usar count() para verificar si un número")
print("   aparece más de una vez en la lista.")
print("\n" + "="*70)
