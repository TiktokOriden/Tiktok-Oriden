@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Oriden Flow - Instalacao Windows
echo ==========================================
echo       ORIDEN FLOW - INSTALACAO
echo ==========================================
echo.
set "PYEXE="
where py >nul 2>nul && set "PYEXE=py -3"
if not defined PYEXE (
  where python >nul 2>nul && set "PYEXE=python"
)
if not defined PYEXE (
  echo Python nao foi encontrado. Tentando instalar via winget...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Instale Python 3.12 em https://www.python.org/downloads/windows/
    echo Marque Add Python to PATH e execute este arquivo novamente.
    pause
    exit /b 1
  )
  winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
  if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  if not defined PYEXE (
    echo Reabra o terminal apos a instalacao e execute este arquivo novamente.
    pause
    exit /b 1
  )
)
echo Usando Python: %PYEXE%
if not exist ".venv\Scripts\python.exe" (
  %PYEXE% -m venv .venv
  if errorlevel 1 goto fail
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo.
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg nao encontrado. O painel abre normalmente, mas videos MP4 exigem FFmpeg.
  echo Para instalar FFmpeg depois, use: winget install --id Gyan.FFmpeg -e
) else (
  echo FFmpeg encontrado: geracao de MP4 disponivel.
)
echo.
echo Instalacao concluida! Abra o arquivo ABRIR-CRM.bat
pause
exit /b 0
:fail
echo Houve uma falha na instalacao. Veja as mensagens acima.
pause
exit /b 1
