# CLAUDE.md: Visualización de Grandes Bases de Datos

Subject context. The repo-wide rules are in the root `CLAUDE.md`; this file adds what was decided for
this subject.

## Subject
- NRC 176458, Thursday (online). Professor: Mtro. Carlos Fernando Ruiz Chávez.
- Class slides in `notas/VGBD_Sesion_NN.pdf`. Each task must follow what the professor showed in the
  matching session (his method, his terms, his example), not a generic approach. Example: Tarea 1.8
  was first done with outlier removal and had to be redone because the class defined noise as
  quantization and showed shared initial centroids.

## Data
- `datos/BD_2024_calidad_aire.xlsx`: SIMAJ air quality 2024. Sheet `Data` = hourly readings per
  station; sheet `Param` = station metadata and coordinates.
- Gotcha: `DATE` already includes the hour. Do not add `HOUR`.
- Country (COU) is closest to home but only has CO for September and no NO2 (tasks 1.0 to 1.2).
  Centro (CEN) has full-year O3, CO and PM, NO2/NO/NOX only September to December (tasks 1.3 on).
  No SIMAJ station measures NO2 before August 2024.
- `datos/datos_1.csv`: "Fenómeno X" coordinates from Session 10 (gitignored, keep a local copy).

## Tasks
- One `tareas/build_tareaNN.py` per task fills `_recursos/plantillas/plantilla_informe_MCD.docx` and
  exports the PDF with LibreOffice into `tareas/Tarea1_N/`. Task 1.0 is `build_tarea10.py`.
- `build_tarea16.py` exports the shared helpers (`add_para`, `add_heading`, `make_table`, `add_apa`,
  `clear_body_after_table1`, colors, `TEMPLATE`, `SOFFICE`, `num`, ...) and the NO2 imputation data;
  1.7, 1.8, 1.9 and Tópicos II Actividad 5 import it.
- Deliverable: `Tarea1_N_VisualizacionGBD_CarlosPulidoRosas.pdf`, copied to Downloads, committed and
  pushed.
- Delivered: 1.0 boxplot/IQR, 1.1 Tukey, 1.2 histogram vs IMECA, 1.3 time series, 1.4 correlation with
  NO2, 1.5 homogeneous corpus + regression through the origin, 1.6 NO2 imputation from CO + multiple
  regression, 1.7 refined regression + PM2.5 vs PM10 K-means, 1.8 quantization + weighted K-means,
  1.9 IMECA norms, binary entropy and CART tree.
- 1.8 detail: the elbow gives k = 5 while the class example uses k = 7; the report presents k = 5 and
  compares with k = 7 in its own section.

## Writing
- Spanish, first person, Carlos's student voice; no em-dashes; avoid repeating a signature phrase
  across tasks (e.g. "Lo que más me llamó la atención" was used in 1.6 and 1.7).
- Every number in the text comes from the script. Explain new variables (what they are and how they
  affect the result); the professor flagged unexplained variables before.
