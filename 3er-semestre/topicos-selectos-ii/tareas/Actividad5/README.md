# Actividad 5 · CNN para clasificación de Pokémon

**Materia:** Tópicos Selectos de Grandes Bases de Datos II (NRC 176456)
**Profesor:** Mtro. Iván Alejandro Toledano Juárez
**Alumno:** Carlos Pulido Rosas

Informe sobre el proyecto del profesor [IvTole/Pokemon_Classification](https://github.com/IvTole/Pokemon_Classification)
(TinyVGG y transferencia de aprendizaje con EfficientNet-B0), con los dos modelos entrenados en una GPU.

## Archivos

| Archivo | Contenido |
|---|---|
| `Actividad5_TopicosGBDII_CarlosPulidoRosas.pdf` | Informe (entregable) |
| `Actividad5_TopicosGBDII_CarlosPulidoRosas.docx` | El mismo informe en Word |
| `entrenar_actividad5.py` | Entrena los cuatro experimentos con el código del profesor (`engine.py`, `TinyVGG`) |
| `figuras_actividad5.py` | Gráficas y resumen por especie |
| `build_actividad5.py` | Arma el informe con la plantilla MCD |
| `resultados/` | Métricas por época (`resultados.json`), predicciones, separación de prueba y figuras |
| `requirements.txt` | Dependencias |

## Cómo reproducirlo

Las imágenes (PokemonData, 151 especies, 11,945 JPG) no se suben al repositorio. Se descargan de
[Hugging Face](https://huggingface.co/datasets/sgtsaughter/pokemon-classification-images-151) y se
descomprimen en `3er-semestre/topicos-selectos-ii/datos/pokemon/PokemonData/`.

```bash
pip install -r requirements.txt   # PyTorch con CUDA: ver https://pytorch.org/get-started/locally/
python entrenar_actividad5.py     # unos 18 minutos en una RTX 4060
python figuras_actividad5.py
python build_actividad5.py        # requiere python-docx y LibreOffice
```

## Resumen de resultados

| Experimento | Exactitud en prueba | Top-5 |
|---|---|---|
| E1 TinyVGG como en el repositorio (prueba copiada del entrenamiento) | 79.7 % | 93.9 % |
| E2 TinyVGG, separación limpia, con aumento de datos, 30 épocas | 57.5 % | 79.8 % |
| E3 TinyVGG, separación limpia, sin aumento de datos, 30 épocas | 42.5 % | 65.2 % |
| E4 EfficientNet-B0 preentrenada, capas convolucionales congeladas, 5 épocas | 77.7 % | 92.2 % |

- `get_data.py` copia (no mueve) las 15 imágenes de prueba por especie, así que también están en el
  entrenamiento: en la época 10 la prueba marca 75.8 % contra 56.4 % con una separación limpia.
- TinyVGG se sobreajusta: la pérdida de prueba es mínima en la época 5; sin aumento de datos el
  entrenamiento llega a 99.8 % y la prueba baja a 42.5 %.
- El 93.6 % de los 1,745,943 parámetros de TinyVGG están en la capa lineal (64 x 13 x 13 = 10,816 entradas).
- EfficientNet-B0 entrena solo 193,431 parámetros y supera a TinyVGG desde la primera época; sus diez
  confusiones más frecuentes son entre especies de la misma línea evolutiva.
