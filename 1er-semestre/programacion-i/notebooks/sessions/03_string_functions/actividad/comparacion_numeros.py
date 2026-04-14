# Ejercicio 1: Comparación de dos números
# Maestria en Ciencia de los Datos
# Programación 1 - Actividad 3
# Autor:  Carlos Pulido Rosas

# Pedir los dos números al usuario
num1 = float(input("Introduce el primer número: "))
num2 = float(input("Introduce el segundo número: "))

# Mostrar los valores introducidos
print(f"Primer número: {num1}")
print(f"Segundo número: {num2}")

# Comparación
if num1 == num2:
    print("Ambos números son iguales.")
elif num1 < num2:
    print("El primer número es menor que el segundo.")
else:
    print("El primer número es mayor que el segundo.")
