"""
Universidad de Guadalajara - CUCEA
Maestria en Ciencia de los Datos
Carlos Pulido Rosas
Programacion I - Clase 9

EJERCICIO 3 - Combinaciones de Blusas y Pantalones
Obtén las combinaciones de blusas y pantalones utilizando listas de comprensión
"""

print("="*70)
print("EJERCICIO 3: COMBINACIONES CON LISTAS DE COMPRENSIÓN")
print("="*70)

# Datos de entrada
blusas = ["Blusa Roja", "Blusa Amarilla"]
pantalones = ["Pantalon Negro", "Pantalon Blanco", "Pantalon Azul"]

print(f"\nBlusas disponibles: {blusas}")
print(f"Pantalones disponibles: {pantalones}")

# ============================================================
# SOLUCIÓN CON CICLOS ANIDADOS (Método tradicional)
# ============================================================

print("\n" + "="*70)
print("MÉTODO 1: CICLOS ANIDADOS (Tradicional)")
print("="*70)

combinaciones_v1 = []

for i in range(len(blusas)):
    for j in range(len(pantalones)):
        combinaciones_v1.append((blusas[i], pantalones[j]))

print("\n Combinaciones encontradas:")
for i, (blusa, pantalon) in enumerate(combinaciones_v1, 1):
    print(f"   {i}. {blusa} + {pantalon}")

print(f"\nTotal de combinaciones: {len(combinaciones_v1)}")

# ============================================================
# SOLUCIÓN CON LISTAS DE COMPRENSIÓN (Lo que se pide)
# ============================================================

print("\n" + "="*70)
print("MÉTODO 2: LISTAS DE COMPRENSIÓN (SOLUCIÓN PEDIDA)")
print("="*70)

# Esta es la solución que se pide en el ejercicio
combinaciones_v2 = [(blusa, pantalon) 
                    for blusa in blusas 
                    for pantalon in pantalones]

print("\nCombinaciones con list comprehension:")
for i, (blusa, pantalon) in enumerate(combinaciones_v2, 1):
    print(f"   {i}. {blusa} + {pantalon}")

print(f"\nTotal de combinaciones: {len(combinaciones_v2)}")

# ============================================================
# VERSIONES ALTERNATIVAS
# ============================================================

print("\n" + "="*70)
print("VERSIONES ALTERNATIVAS DE LIST COMPREHENSION")
print("="*70)

# Versión 1: En una sola línea (más compacta)
combinaciones_v3 = [(b, p) for b in blusas for p in pantalones]
print("\nVersión compacta (una línea):")
print(f"   {combinaciones_v3}")

# Versión 2: Con índices
combinaciones_v4 = [(blusas[i], pantalones[j]) 
                    for i in range(len(blusas)) 
                    for j in range(len(pantalones))]
print("\nVersión con índices:")
for combo in combinaciones_v4:
    print(f"   {combo}")

# Versión 3: Como diccionarios
combinaciones_v5 = [{"blusa": b, "pantalon": p} 
                    for b in blusas 
                    for p in pantalones]
print("\nVersión con diccionarios:")
for i, combo in enumerate(combinaciones_v5, 1):
    print(f"   {i}. {combo}")

# Versión 4: Como strings (para imprimir bonito)
combinaciones_v6 = [f"{b} con {p}" 
                    for b in blusas 
                    for p in pantalones]
print("\nVersión con strings formateados:")
for outfit in combinaciones_v6:
    print(f" {outfit}")

# ============================================================
# EJEMPLO NUMÉRICO (Como en clase)
# ============================================================

print("\n" + "="*70)
print("EJEMPLO NUMÉRICO (Como en el notebook)")
print("="*70)

# Ejemplo con números del notebook
lista_pares_tradicional = []
for i in range(1, 3):
    for j in range(1, 5):
        lista_pares_tradicional.append((i, j))

print("\nCon ciclos tradicionales:")
print(f"   {lista_pares_tradicional}")

# Con list comprehension
lista_pares_comprehension = [(i, j) for i in range(1, 3) for j in range(1, 5)]
print("\nCon list comprehension:")
print(f"   {lista_pares_comprehension}")

# ============================================================
# EJEMPLO ADICIONAL: MÁS PRENDAS
# ============================================================

print("\n" + "="*70)
print("EJEMPLO ADICIONAL: GUARDARROPA COMPLETO")
print("="*70)

# Más opciones de ropa
blusas_ext = ["Blusa Roja", "Blusa Amarilla", "Blusa Verde", "Blusa Azul"]
pantalones_ext = ["Pantalon Negro", "Pantalon Blanco", "Pantalon Azul", "Pantalon Gris"]
zapatos = ["Zapatos Negros", "Zapatos Cafes", "Zapatos Blancos"]

print(f"\nBlusas: {len(blusas_ext)}")
print(f"Pantalones: {len(pantalones_ext)}")
print(f"Zapatos: {len(zapatos)}")

# Combinaciones de 2 prendas
combinaciones_2_prendas = [(b, p) 
                           for b in blusas_ext 
                           for p in pantalones_ext]
print(f"\nCombinaciones de 2 prendas: {len(combinaciones_2_prendas)}")

# Combinaciones de 3 prendas (outfit completo)
combinaciones_3_prendas = [(b, p, z) 
                           for b in blusas_ext 
                           for p in pantalones_ext 
                           for z in zapatos]
print(f"Combinaciones de 3 prendas: {len(combinaciones_3_prendas)}")

print("\nEjemplos de outfits completos:")
for i, (blusa, pantalon, zapato) in enumerate(combinaciones_3_prendas[:5], 1):
    print(f"   {i}. {blusa} + {pantalon} + {zapato}")
print(f"   ... y {len(combinaciones_3_prendas) - 5} combinaciones más!")

# ============================================================
# COMPARACIÓN DE SINTAXIS
# ============================================================

print("\n" + "="*70)
print("COMPARACIÓN: CICLOS vs LIST COMPREHENSION")
print("="*70)

print("\nCON CICLOS ANIDADOS:")
print("""
combinaciones = []
for blusa in blusas:
    for pantalon in pantalones:
        combinaciones.append((blusa, pantalon))
""")

print("CON LIST COMPREHENSION:")
print("""
combinaciones = [(blusa, pantalon) 
                 for blusa in blusas 
                 for pantalon in pantalones]
""")

print("\nVENTAJAS DE LIST COMPREHENSION:")
print("   ✅ Más conciso (menos líneas)")
print("   ✅ Más rápido de ejecutar")
print("   ✅ Más 'pythonic' (estilo Python)")
print("   ✅ Más fácil de leer una vez que lo dominas")

print("\n" + "="*70)
print("\nLa estructura de list comprehension para combinaciones es:")
print("   [(item1, item2) for item1 in lista1 for item2 in lista2]")
print("\n" + "="*70)
