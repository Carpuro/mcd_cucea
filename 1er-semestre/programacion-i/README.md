# 📊 MCD Programación 1 – Dockerized Python Sessions

This repository contains Python exercises for MCD Programación 1, packaged in a Docker environment so you can run everything without installing Python or extra libraries on your computer.

We use Python 3.11, with key data science libraries like:

pandas – for data handling

matplotlib – for visualizations

# 🚀 Quick Start

1. Clone this repository

    Download the project to your computer:

    git clone <repo_url>
    cd MCD_PROGRAMACION_1

2. Build the Docker image

    Run this once to prepare the environment:

    docker build -t mcd_prog1:latest .


This step creates a container image called "mcd_prog1" with all the dependencies ready.

3. Run a session program

    Each session is in:

    sessions/<nn_topic>/<program>.py


For example, to run Session 1 – Histogramas:

docker run --rm ^
  -v "${PWD}\data:/app/data" ^
  -v "${PWD}\output:/app/output" ^
  mcd_prog1:latest \
  python sessions/01_histogramas/Histogramas_Python.py \
    --csv data/categorias_de_corredores.csv


# Notes:

--csv points to the CSV file you want to process.

data/ and output/ are mounted so files can be shared between your computer and Docker.

# 📂 Folder Structure

📦 MCD_Programacion_1
 ┣ 📂 common           → helper functions (e.g., path handling)
 ┣ 📂 data             → CSV and input files
 ┣ 📂 output           → generated plots / results
 ┣ 📂 sessions         → exercises (one folder per topic)
 ┣ 📜 Dockerfile       → Docker build instructions
 ┗ 📜 requirements.txt → Python dependencies

# 🖱 One-Click Execution (Windows)

If you don’t want to type commands, use the provided .bat or .ps1 script in each session folder.
These scripts will:

Build the image (if needed)

Run the selected session

Save the results into output/

Example for Session 1:

Double-click Run_Histogramas.bat (Windows) or

Right-click → “Run with PowerShell” on Run_Histogramas.ps1

# ✅ Tips

Make sure Docker Desktop is running before executing commands.

Always place your CSV files inside the data/ folder so the container can access them.

Results (plots, CSV summaries) will be in output/.