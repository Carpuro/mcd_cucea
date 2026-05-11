# Actividad 7 — Instalación de paquetes bigmemory y ff en R

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** R 4.5.3 · RStudio 2025.05.0

## Objetivo

Instalar y verificar los paquetes `bigmemory` y `ff` en R, que implementan dos estrategias distintas para trabajar con grandes bases de datos en equipo local: **memoria compartida** y **archivos de mapa de memoria**.

## Paquetes instalados

| Paquete | Versión | Estrategia | Descripción |
|---------|---------|------------|-------------|
| `bigmemory` | 4.6.4 | Memoria compartida | Matrices fuera del heap de R — acceso concurrente entre procesos |
| `ff` | 4.5.2 | Memory-mapped files | Datos en disco accedidos como si fueran RAM |

## Instalación

```r
install.packages(c("bigmemory", "ff"), repos = "https://cran.rstudio.com/")
```

**Dependencias instaladas automáticamente:**

| Paquete | Versión | Requerido por |
|---------|---------|---------------|
| `bigmemory.sri` | 0.1.8 | bigmemory |
| `Rcpp` | 1.1.1 | bigmemory |
| `uuid` | 1.2-2 | bigmemory |
| `BH` | 1.90.0 | bigmemory |
| `bit` | 4.6.0 | ff |

## Verificación de versiones

```r
packageVersion("bigmemory")  # '4.6.4'
packageVersion("ff")         # '4.5.2'
```

## Ejemplo — bigmemory

```r
library(bigmemory)

# Crear matriz de 1,000 x 5 en memoria compartida
bm <- big.matrix(nrow=1000, ncol=5, type="double", init=0)
bm[1:3, 1:3] <- matrix(1:9, 3, 3)

cat("Clase:", class(bm))         # big.matrix
cat("Dimensiones:", nrow(bm), "x", ncol(bm))  # 1000 x 5
print(bm[1:3, 1:3])

# Compartir con otros procesos R
desc <- describe(bm)
# En otro proceso: bm2 <- attach.big.matrix(desc)
```

## Ejemplo — ff

```r
library(ff)

# Vector de 10,000 enteros mapeado a disco
ffv <- ff(1:10000, filename=tempfile(fileext=".ff"), vmode="integer")

cat("Longitud:", length(ffv))                          # 10000
cat("Primeros 5:", ffv[1:5])                           # 1 2 3 4 5
cat("Suma:", sum(ffv[]))                               # 50005000
cat("Tamaño en disco:", file.info(filename(ffv))$size) # 40000 bytes

close(ffv)
```

## Comparación de estrategias

| Característica | bigmemory | ff |
|----------------|-----------|-----|
| Ubicación datos | RAM / shared memory | Archivo binario en disco |
| Acceso concurrente | Sí — múltiples procesos R | Limitado |
| Persistencia | Opcional (backing file) | Sí — el archivo permanece |
| Estructura | Matrices (`big.matrix`) | Vectores, matrices, `ffdf` |
| Uso típico | Cómputo paralelo | Datasets que no caben en RAM |

## Screenshots

| Archivo | Contenido |
|---------|-----------|
| `screenshots/ss1_instalacion.png` | Consola RStudio — instalación completa de ambos paquetes |
| `screenshots/ss2_ejecucion.png` | Consola RStudio — ejecución de ejemplos bigmemory y ff |

## Generación del reporte

```bash
# En entorno MCD de Anaconda (Windows)
conda activate MCD
python generar_reporte.py
```

## Entregable

`Actividad_R_Tarea7_CarlosPulidoRosas.pdf`
