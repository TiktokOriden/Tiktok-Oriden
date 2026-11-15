@echo off
setlocal
cd /d "%~dp0"
title Oriden Flow - CRM
if not exist ".venv\Scripts\python.exe" (
  echo Primeiro execute INSTALAR-WINDOWS.bat.
  pause
  exit /b 1
)
echo Iniciando Oriden Flow em http://127.0.0.1:8000
echo Mantenha esta janela aberta enquanto usar o CRM.
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
echo.
echo O servidor foi encerrado. Verifique erros acima.
pause
