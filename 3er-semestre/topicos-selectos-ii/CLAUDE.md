# CLAUDE.md: Tópicos Selectos de GBD II

Subject context. The repo-wide rules are in the root `CLAUDE.md`; this file adds what was decided for
this subject.

## Subject
- NRC 176456, Tuesday (online). Professor: Mtro. Iván Alejandro Toledano Juárez.
- Course material: https://github.com/IvTole/Topicos_Selectos_II_CUCEA (marimo notebooks, one folder
  per topic). Activities are posted in Classroom with links to his notebooks or repos.
- The professor told Carlos that the deliverable plus the repo folder link is enough, so every
  activity folder must be ready for him to browse on GitHub (README first, results visible).
  The repo is public for that reason.

## How activities are done
- Start from the professor's notebook, keep his code and his questions, and answer them with
  experiments that reuse his functions with fixed settings (his widgets only show one case).
- Write as Carlos: Spanish, first person, natural and mature student voice, no em-dashes, no stock AI
  phrases ("No me quise quedar en...", "Lo más importante que saqué", "Primero/Segundo/Tercero"
  lists, colon reveals). Aim for a full 100: answer every question explicitly.
- Every number in the text must match what the notebook or script computes. Re-check claims after
  any rerun.
- Naming: `ActividadN_TopicosGBDII_CarlosPulidoRosas.py` (same convention as Visualización). Two
  notebooks in one topic: `ActividadN_1_...`, `ActividadN_2_...`.
- Notebook deliverables (Actividades 1 to 4): marimo `.py` (the deliverable), `.ipynb` exported with
  outputs and kernelspec set, `.html`, `README.md`, `requirements.txt` (marimo 0.25.1, numpy 2.3.5,
  matplotlib 3.10.1, scikit-learn 1.8.0, jupyter).
  - Export: `conda run -n MCD marimo export ipynb <f>.py -o <f>.ipynb --include-outputs -f` and
    `marimo export html`; verify with `marimo check` and `jupyter nbconvert --execute`.
  - marimo gotchas: `@app.function` needs imports in `with app.setup:`; variable names must be unique
    across cells (use `_` prefix for locals).
  - Use the `tabla_md` markdown helper, not `mo.ui.table`, so tables render in Jupyter and GitHub.
  - No `.gitkeep` files inside activity folders.

## Actividad 5 (CNN Pokémon), delivered 2026-11-17
- Classmates confirmed it was "solo un informe", so it is a PDF report on the MCD template, not a
  notebook. Professor's repo: IvTole/Pokemon_Classification (TinyVGG, `src/` modular code; molab
  notebook = same code, 10 epochs; extra notebook with EfficientNet-B0 transfer learning).
- Scripts: `entrenar_actividad5.py` (env `torch`, GPU), `figuras_actividad5.py` (env `torch`),
  `build_actividad5.py` (env `MCD`, imports the Visualización template helpers).
- Data: PokemonData from Hugging Face (sgtsaughter), 11,945 images, 151 classes, in
  `datos/pokemon/` (gitignored). Kaggle needs a login, so it was not used.
- Experiments: E1 repo as is (`get_data.py` copies test images, so they leak into train), E2 clean
  split + augmentation, E3 clean split no augmentation, E4 EfficientNet-B0 frozen features.
  E2 to E4 are deterministic across reruns; E1 is not (it changed from 75.8 % to 81.6 % at epoch 10
  between runs). Weights saved in `tareas/Actividad5/models/` (gitignored `*.pth`).
- The report includes the console training output, prediction grids with softmax probabilities and
  top-5 bars, because Carlos wanted to see the models working, not only metrics.

## Environment
- PyTorch lives in its own conda env `torch` (torch 2.14.1+cu126, RTX 4060). Installing pip torch in
  `MCD` breaks with conda's MKL OpenMP DLLs; do not do it.
- Run envs with `C:\Users\carlo\anaconda3\Scripts\conda.exe run -n <env> python <file>` (direct
  `python.exe` from an env fails with rc 127; `conda run` rejects `-c` code with newlines, so write a
  file).

## Proyecto final (SSD300 object detection), team project, 2026-11-26
- Repo base: sgrvinod/a-PyTorch-Tutorial-to-Object-Detection. Team: one member trained in Modal
  (epochs 83 to 190, best = epoch 160, mAP 75.19 %), another built the marimo app on molab
  (nb_9o5HDcMtHPxcr5FNwajrGh/app). Carlos wrote the report. Carlos asked to keep member names OUT of
  the report (no participation table).
- Folder `proyectos/ProyectoFinal_SSD300/`: `codigo/evaluar_ssd.py` (torch env, resumable steps),
  `figuras_ssd.py` (torch env), `build_reporte.py` (MCD env). Checkpoints in `modelos/` and VOC2007
  test in `datos/voc/` are gitignored. Source zips in `Downloads\RCNN`.
- Local check on RTX 4060: epoch 160 = 75.19 % (matches Modal), professor's epoch 83 = 66.91 %.
  NMS experiment on first 1,000 test images: 0.30 -> 74.63 %, 0.45 -> 75.55 %, 0.60 -> 74.04 %.
- The repo's `calculate_mAP` mixes CPU/GPU tensors and syncs per detection; `calc_map_rapido` gives
  identical results (verified, uses float32 like the repo; float64 changes the 0.9 recall threshold).
- Low RAM (16 GB): Claude Code reaps background jobs; run long evals as a detached Start-Process with
  num_workers=1. A full VOC test pass takes ~11 to 23 min on the laptop.
- matplotlib in the torch env does not draw plain text or bbox text over imshow; use path_effects.
