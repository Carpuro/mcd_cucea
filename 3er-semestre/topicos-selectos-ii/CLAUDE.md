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
