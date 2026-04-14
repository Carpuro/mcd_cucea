# Maestria en Ciencia de los Datos
## Metodos Estadisticos Basicos - Carlos Pulido Rosas
## Actividad 4 - Probabilidad

# Importamos Librerias
import os
import pandas as pd
import numpy as np

# Importamos el dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "emails_spam_sample.csv")
print("Cargando desde:", csv_path)
df = pd.read_csv(csv_path)
print(df)


# Datos de Pregunta 1
P_A_given_B = 0.9      # P(A|B)
P_B = 0.05             # P(B)
P_A = 0.45             # P(A)

# Teorema de Bayes: P(B|A) = P(A|B) * P(B) / P(A)
P_B_given_A = (P_A_given_B * P_B) / P_A
print("Pregunta 1:")
print("La probabilidad de tener la enfermedad B dado que el gen A está activo es:", P_B_given_A)


# Datos de Pregunta 2

# Probabilidad base
P_car = 0.30
P_walk = 0.30
P_bus = 0.40

# Probabilidades de llegar tarde dado el modo de transporte
P_late_given_walk = 0.10
P_late_given_car = 0.03
P_late_given_bus = 0.07

# Probabilidad total de llegar tarde (ley de la probabilidad total)
P_late = (
    P_walk * P_late_given_walk + # Llegar tarde caminando
    P_car * P_late_given_car +   # Llegar tarde en carro
    P_bus * P_late_given_bus     # Llegar tarde en bus
)

# Bayes: probabilidad de que haya tomado el camión dado que llegó tarde
P_bus_given_late = (P_bus * P_late_given_bus) / P_late

print("\nPregunta 2:")
print(f"Probabilidad de que haya tomado el camión dado que llegó tarde: {P_bus_given_late:.4f}")

# --- Pregunta 2: P(Walk | On Time) ---

# Probabilidad de llegar a tiempo dado cada transporte
P_on_time_given_walk = 1 - P_late_given_walk
P_on_time_given_car = 1 - P_late_given_car
P_on_time_given_bus = 1 - P_late_given_bus

# Probabilidad total de llegar a tiempo
P_on_time = (
    P_walk * P_on_time_given_walk +
    P_car * P_on_time_given_car +
    P_bus * P_on_time_given_bus
)

# Bayes: probabilidad de que haya caminado dado que llegó a tiempo
P_walk_given_on_time = (P_walk * P_on_time_given_walk) / P_on_time

print(f"Probabilidad de que haya caminado dado que llegó a tiempo: {P_walk_given_on_time:.4f}")

