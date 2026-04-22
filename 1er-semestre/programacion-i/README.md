# Programación I
**Semestre:** 1ro | **Departamento:** DSI | **Créditos:** 7 | **Estado:** ✅ Terminado

Fundamentos de programación en Python para ciencia de datos: estructuras del lenguaje, manejo de archivos, web scraping, conectividad con bases de datos e interfaces gráficas. Las sesiones corren en un entorno Dockerizado.

## Sesiones (`notebooks/sessions/`)

| # | Tema | Estado |
|---|------|--------|
| 01 | Arquitectura de Python | ✅ Hecho |
| 02 | Fundamentos de Python | ✅ Hecho |
| 03 | Funciones de cadenas | ✅ Hecho |
| 04 | Manejo de archivos | ✅ Hecho |
| 05 | Estructuras de datos | ✅ Hecho |
| 06 | Expresiones regulares | ✅ Hecho |
| 07 | Archivos externos (Excel, CSV, JSON) | ✅ Hecho |
| 08 | Sockets y servicios web | ✅ Hecho |
| 09 | Web scraping (Selenium) | ✅ Hecho |
| 10 | Interfaces gráficas (tkinter) | ✅ Hecho |
| 11 | SQL en Python (Parte 1) | ✅ Hecho |
| 12 | SQL en Python (Parte 2) | ✅ Hecho |
| 13 | MySQL en Python | ✅ Hecho |
| 14 | Combinar interfaces gráficas y bases de datos | ✅ Hecho |

## Inicio rápido (Docker)

```bash
docker build -t mcd_prog1:latest .
docker run --rm \
  -v "${PWD}/datos/data:/app/data" \
  -v "${PWD}/tareas/output:/app/output" \
  mcd_prog1:latest \
  python sessions/01_python_architecture/<script>.py
```

## Estructura
- `notebooks/sessions/` — una carpeta por sesión con ejercicios
- `notebooks/common/` — funciones de apoyo compartidas
- `datos/data/` — archivos CSV de entrada
- `tareas/output/` — gráficas y resultados generados
- `notas/presentation/` — diapositivas (Selenium, Interfaces gráficas)

## Herramientas
Python 3.11 · Docker · pandas · matplotlib · Selenium · MySQL
