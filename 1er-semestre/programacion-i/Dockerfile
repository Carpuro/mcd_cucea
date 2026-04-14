# Dockerfile
FROM python:3.11-slim

# Paquetes mínimos para matplotlib (fuentes) y tzdata (evitar warnings)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencias de Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY common/   /app/common/
COPY sessions/ /app/sessions/

# Asegurar que Python vea /app como raíz para importar "common"
ENV PYTHONPATH=/app

# Ejecuta tu script por defecto y permite pasar argumentos tras la imagen
ENTRYPOINT ["python", "sessions/01_histogramas/Histogramas_Python.py"]
# CSV por defecto (se puede sobreescribir con args en docker run)
CMD ["--csv", "data/categorias_de_corredores.csv"]