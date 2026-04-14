# MCD CUCEA — Maestría en Ciencias de los Datos
**Universidad de Guadalajara · Centro Universitario de Ciencias Económico Administrativas**

Repositorio central con todo el material de trabajo del programa MCD — organizado por semestre y materia.

---

## Estructura

```
mcd_cucea/
├── _recursos/
│   ├── programas/          ← PDFs oficiales de los 16 programas de materia
│   ├── plantillas/         ← plantilla_informe_MCD.docx (navy/amber)
│   ├── logos/              ← logos UdeG
│   └── plan-de-estudios.md ← plan completo con créditos y pre-requisitos
├── 1er-semestre/
├── 2do-semestre/
├── 3er-semestre/
└── 4to-semestre/
```

Cada materia sigue la misma estructura interna:
```
materia/
├── notebooks/   ← ejercicios y notebooks
├── tareas/      ← entregas formales
├── proyectos/   ← proyectos parciales o finales
├── datos/       ← datasets específicos de la materia
├── notas/       ← slides, lecturas, material del profesor
└── README.md
```

---

## Primer Semestre

| Materia | Contenido |
|---------|-----------|
| [Métodos Estadísticos Básicos](1er-semestre/metodos-estadisticos-basicos/) | Estadística descriptiva, regresión, clustering, probabilidad, distribuciones, pruebas de hipótesis |
| [Métodos Matemáticos para el Análisis de Datos](1er-semestre/metodos-matematicos-analisis-datos/) | Álgebra lineal, optimización, visión computacional, algoritmos evolutivos |
| [Procesamiento de Grandes Bases de Datos](1er-semestre/procesamiento-grandes-bases-datos/) | Apache Spark, PySpark, Koalas, Spark ML, Spark Streaming |
| [Programación I](1er-semestre/programacion-i/) | Python fundamentals, web scraping, SQL, GUIs — entorno Docker |

## Segundo Semestre

| Materia | Contenido |
|---------|-----------|
| [Almacenamiento de Grandes Bases de Datos](2do-semestre/almacenamiento/) | Hadoop 3.3.6, Hive 2.3.2, MapReduce, datos IMSS ASG 2025 |
| [Métodos Estadísticos Multivariados](2do-semestre/metodos-estadisticos-multivariados/) | Análisis multivariado, MANOVA, análisis discriminante |
| [Programación II](2do-semestre/programacion-ii/) | Python avanzado, SQL Server, stored procedures, dataset Defunciones_2000 |
| [Tópicos Selectos de GBD I](2do-semestre/topicos-selectos-i/) | Tópicos avanzados de gestión de grandes bases de datos |

## Tercer Semestre *(próximo)*

| Materia |
|---------|
| Econometría |
| Visualización de Grandes Bases de Datos |
| Desarrollo de Proyecto I |
| Tópicos Selectos de GBD II |

## Cuarto Semestre *(próximo)*

| Materia |
|---------|
| Seminario de Tesis |
| Tópicos Complementarios de Gestión de Datos |
| Desarrollo de Proyecto II |
| Tópicos Selectos de GBD III |

---

## Infraestructura (Homelab)

| Servicio | Acceso |
|----------|--------|
| Hadoop HDFS UI | `http://192.168.100.11:9870` |
| YARN UI | `http://192.168.100.11:8088` |
| HiveServer2 | `192.168.100.11:10000` (Tailscale: `100.64.0.11:10000`) |
| SQL Server 2025 | `100.64.0.11,1433` · user: `readonly` / `MCD_2000` |

**Acceso remoto:** instalar [Tailscale](https://tailscale.com/download) y solicitar acceso.

---

## Recursos

- [Plan de estudios completo](_recursos/plan-de-estudios.md)
- [Programas de materia](_recursos/programas/)
- [Plantilla de informes](_recursos/plantillas/plantilla_informe_MCD.docx)
