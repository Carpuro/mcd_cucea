@echo off
setlocal EnableExtensions

REM --- Config ---
set IMAGE_NAME=mcd_prog1:latest
REM Usa slashes para rutas que verá el contenedor (Linux)
set CSV_REL=data/categorias_de_corredores.csv
set OUTPUT_REL=output
REM -------------


REM Move to this script's folder
cd /d "%~dp0"

REM Compute repo root (two levels up: 01_histogramas -> sessions -> MCD_PROGRAMACION_1)
set "REPO_ROOT=%cd%\..\.."

REM 1) Check Docker is available
where docker >nul 2>nul
if errorlevel 1 (
  echo Docker is not installed or not in PATH.
  echo Install Docker Desktop and try again.
  pause
  exit /b 1
)

REM 2) Check CSV exists on host (usa backslashes para Windows host)
if not exist "%REPO_ROOT%\data\categorias_de_corredores.csv" (
  echo CSV not found: "%REPO_ROOT%\data\categorias_de_corredores.csv"
  echo Put your CSV under "data\" or edit CSV_REL in this .bat file.
  pause
  exit /b 1
)

REM 3) Ensure output folder exists
if not exist "%REPO_ROOT%\%OUTPUT_REL%" mkdir "%REPO_ROOT%\%OUTPUT_REL%" >nul 2>nul

REM 4) Build image (context = repo root)
echo Building Docker image: %IMAGE_NAME%
pushd "%REPO_ROOT%"
docker build -t %IMAGE_NAME% .
if errorlevel 1 (
  echo Build failed.
  popd
  pause
  exit /b 1
)

REM 5) Run container (mount data/output; container paths usan slashes)
echo Running container...
docker run --rm ^
  -v "%REPO_ROOT%\data:/app/data" ^
  -v "%REPO_ROOT%\output:/app/output" ^
  %IMAGE_NAME% --csv "%CSV_REL%"
set EXITCODE=%ERRORLEVEL%
popd

if %EXITCODE% neq 0 (
  echo Container run failed with exit code %EXITCODE%.
  pause
  exit /b %EXITCODE%
)

REM 6) Open output folder
if exist "%REPO_ROOT%\%OUTPUT_REL%\01_histogramas\docker" (
  start "" explorer.exe "%REPO_ROOT%\%OUTPUT_REL%\01_histogramas\docker"
) else (
  start "" explorer.exe "%REPO_ROOT%\%OUTPUT_REL%"
)

echo Done.
pause