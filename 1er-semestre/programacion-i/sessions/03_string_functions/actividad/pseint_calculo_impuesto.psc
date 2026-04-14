Algoritmo Tasa_Impuesto
	
    Definir opcion Como Entero
	
    Escribir "=== Cálculo de Tasa de Impuesto ==="
    Escribir "Seleccione la opción de acuerdo a su ingreso:"
    Escribir "1) $0 a $5,000         ?  $0 pesos"
    Escribir "2) $5,001 a $10,000    ?  $114.20 pesos"
    Escribir "3) $10,001 a $15,000   ?  $2,970 pesos"
    Escribir "4) $15,001 a $20,000   ?  $7,130 pesos"
    Escribir "5) $20,001 a $25,000   ?  $9,438 pesos"
	
    Escribir "Introduce el número de la opción (1-5): "
    Leer opcion
	
    Segun opcion Hacer
        1:
            Escribir "La cuota a pagar es: $0.00 pesos"
        2:
            Escribir "La cuota a pagar es: $114.20 pesos"
        3:
            Escribir "La cuota a pagar es: $2,970.00 pesos"
        4:
            Escribir "La cuota a pagar es: $7,130.00 pesos"
        5:
            Escribir "La cuota a pagar es: $9,438.00 pesos"
        De Otro Modo:
            Escribir "Opción inválida. Por favor selecciona un número entre 1 y 5."
    FinSegun
	
FinAlgoritmo
