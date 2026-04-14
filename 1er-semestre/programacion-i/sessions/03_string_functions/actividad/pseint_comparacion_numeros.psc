Algoritmo Comparacion_De_Dos_Numeros
	// Declaración de variables
	Definir num1, num2 Como Real
	// Entrada de datos
	Escribir 'Introduce el primer número: '
	Leer num1
	Escribir 'Introduce el segundo número: '
	Leer num2
	// Mostrar los valores introducidos
	Escribir 'Primer número: ', num1
	Escribir 'Segundo número: ', num2
	// Comparación de los números
	Si num1=num2 Entonces
		Escribir 'Ambos números son iguales.'
	SiNo
		Si num1<num2 Entonces
			Escribir 'El primer número es menor que el segundo.'
		SiNo
			Escribir 'El primer número es mayor que el segundo.'
		FinSi
	FinSi
FinAlgoritmo
