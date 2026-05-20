# Actividad 3 — Instalación y Configuración de Apache Hive

**Materia:** Almacenamiento de Grandes Bases de Datos  
**Módulo:** Apache Hive  
**Alumno:** Carlos Pulido Rosas  
**Herramienta:** Apache Hive 2.3.2 + Hadoop 3.3.6 (Docker Compose)

## Objetivo

Instalar y configurar Apache Hive sobre el clúster Hadoop existente usando Docker Compose, con metastore persistente en PostgreSQL y ruta HDFS propia fuera de `/tmp`.

## Stack Docker

```yaml
hive-server:        # HiveServer2 — puerto 10000 (JDBC) y 10002 (Web UI)
hive-metastore:     # Thrift Metastore Service
hive-metastore-db:  # PostgreSQL 9.6 — almacena el catálogo de tablas
```

Además de los contenedores Hadoop previos:
```yaml
hadoop-namenode     # HDFS NameNode — puerto 9870
hadoop-datanode     # HDFS DataNode
hadoop-resourcemanager  # YARN — puerto 8088
hadoop-nodemanager
```

## Configuración clave

- **Ruta HDFS:** `/user/oem/` (persistente, fuera de `/tmp` que se limpia al reiniciar)
- **Metastore:** PostgreSQL 9.6 en contenedor `hive-metastore-db`
- **Conexión beeline:**

```bash
docker exec -i hive-server beeline \
  -u 'jdbc:hive2://localhost:10000' \
  --silent=true 2>/dev/null
```

## Verificación

```sql
SHOW DATABASES;
-- default
CREATE DATABASE prueba;
SHOW DATABASES;
-- default, prueba
DROP DATABASE prueba;
```

## Entregable

`Actividad_Instalacion_Hive_CarlosPulidoRosas.pdf`
