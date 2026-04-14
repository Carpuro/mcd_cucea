Algoritmo Reloj_Digital
	Definir horas, minutos, segs Como Entero
	horas <- 0
	minutos <- 59
	segs <- 50
	Mientras Verdadero Hacer
		Limpiar Pantalla // para que parezca un reloj real
		// Mostrar horas con formato 2 dígitos
		Si horas<10 Entonces
			Escribir '0'Sin Saltar
		FinSi
		Escribir horas, ':'Sin Saltar
		// Mostrar minutos con formato 2 dígitos
		Si minutos<10 Entonces
			Escribir '0'Sin Saltar
		FinSi
		Escribir minutos, ':'Sin Saltar
		// Mostrar segundos con formato 2 dígitos
		Si segs<10 Entonces
			Escribir '0'Sin Saltar
		FinSi
		Escribir segs
		// Incrementar el tiempo
		segs <- segs+1
		Si segs=60 Entonces
			segs <- 0
			minutos <- minutos+1
			Si minutos=60 Entonces
				minutos <- 0
				horas <- horas+1
				Si horas=24 Entonces
					horas <- 0
				FinSi
			FinSi
		FinSi
		Esperar 1 Segundos
	FinMientras
FinAlgoritmo
