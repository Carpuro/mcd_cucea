# Ejercicio 2: Desplegando la Tasa de Impuesto

print("=== Cálculo de Tasa de Impuesto ===")
print("Seleccione la opción de acuerdo a su ingreso:")
print("1) $0 a $5,000         →  $0 pesos")
print("2) $5,001 a $10,000    →  $114.20 pesos")
print("3) $10,001 a $15,000   →  $2,970 pesos")
print("4) $15,001 a $20,000   →  $7,130 pesos")
print("5) $20,001 a $25,000   →  $9,438 pesos")

# Pedir opción al usuario
opcion = int(input("Introduce el número de la opción (1-5): "))

# Diccionario de tarifas
tarifas = {
    1: 0.00,
    2: 114.20,
    3: 2970.00,
    4: 7130.00,
    5: 9438.00
}

# Verificar si la opción es válida
if opcion in tarifas:
    print(f"La cuota a pagar es: ${tarifas[opcion]:,.2f} pesos")
else:
    print("Opción inválida. Por favor selecciona un número entre 1 y 5.")
