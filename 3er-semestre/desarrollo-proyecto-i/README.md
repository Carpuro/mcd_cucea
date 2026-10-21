# Desarrollo de Proyecto I
**Semestre:** 3ro | **Departamento:** DSI | **Créditos:** 7
**Profesora:** Dra. Ana Rosa Jiménez Meza | **NRC:** 176459 | **Día:** miércoles (en línea)

Materia de avance del trabajo recepcional (tesis): protocolo de investigación, revisión de
literatura y avance para el coloquio. La tesis está en el repositorio
[ai-automation-risk-jalisco](https://github.com/Carpuro/ai-automation-risk-jalisco).

## Entregables (`tareas/`)

| Entregable | Contenido | Carpeta |
|---|---|---|
| Protocolo de investigación | Protocolo sobre la plantilla oficial del CUCEA, con lineamientos MCD Ver. 2.0 y referencias en APA 7 | [Protocolo](tareas/Protocolo/) |
| Análisis de referencias | 16 referencias con tabla de análisis, búsqueda en Consensus y PDFs de las fuentes | [Actividad_Referencias](tareas/Actividad_Referencias/) |

### Protocolo (`tareas/Protocolo/`)
- `build_protocolo.py` llena la plantilla oficial (`plantilla_protocolo_cucea_2026.docx`) conservando
  portada, logos y pie de página; el texto está en `contenido_protocolo.py`.
- `fuentes/` guarda los documentos de donde salen los datos citados (INEGI, IFR, Banxico, SE).

### Análisis de referencias (`tareas/Actividad_Referencias/`)
- `build_referencias.py` genera el análisis (DOCX y PDF) y la tabla en Excel.
- `referencias/` tiene los 16 artículos numerados en orden cronológico.
- `consensus/` tiene la respuesta y las referencias exportadas de la búsqueda en Consensus.

## Herramientas

Python · python-docx · pdfplumber · LibreOffice · Consensus · NotebookLM
