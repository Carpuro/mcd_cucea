# Actividad 1 — WordCount con Hadoop MapReduce

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Apache Hadoop 3.3.6 (MapReduce + HDFS)

## Objetivo

Ejecutar el job clásico de WordCount sobre el texto completo de *War and Peace* (Tolstói) usando el framework MapReduce de Hadoop sobre HDFS.

## Archivo de entrada

| Archivo | Descripción |
|---------|-------------|
| `warandpeace.txt` | Texto completo de *Guerra y Paz* — ~3.2 MB, ~560,000 palabras |

## Proceso

1. Subir `warandpeace.txt` a HDFS: `/user/oem/input/`
2. Ejecutar el job MapReduce de WordCount incluido en Hadoop
3. Leer el resultado desde HDFS: `/user/oem/output/`
4. Exportar `resultado.txt` con la frecuencia de cada palabra

## Comandos principales

```bash
# Subir archivo a HDFS
docker exec hadoop-namenode hdfs dfs -put warandpeace.txt /user/oem/input/

# Ejecutar WordCount
docker exec hadoop-namenode hadoop jar \
  /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar \
  wordcount /user/oem/input /user/oem/output

# Leer resultado
docker exec hadoop-namenode hdfs dfs -cat /user/oem/output/part-r-00000
```

## Resultado

- **Archivo:** `resultado.txt`
- Contiene cada palabra única del texto y su frecuencia de aparición
- Las palabras más frecuentes son artículos y preposiciones en inglés (the, and, of…)

## Entregable

`Actividad_HadoopMapReduce_WordCount_CarlosPulidoRosas.pdf`
