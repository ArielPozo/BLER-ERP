@echo off
setlocal EnableExtensions
chcp 65001 >nul
title BLER ERP - Detener demo
cd /d "%~dp0"

docker info >nul 2>&1
if errorlevel 1 (
    echo  Docker no está en marcha: la demo ya está detenida.
    goto :end
)
echo  Deteniendo BLER ERP (los datos se conservan)...
docker compose -f docker-compose.yml stop
echo.
echo  Demo detenida. Para volver a usarla, ejecute iniciar_demo.bat

:end
echo.
pause
