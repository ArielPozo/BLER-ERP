@echo off
setlocal EnableExtensions
chcp 65001 >nul
title BLER ERP - Reiniciar demo
cd /d "%~dp0"

echo.
echo  Esto BORRA todos los datos de la demo (clientes, vehículos, órdenes y
echo  cualquier cambio que haya hecho) y la deja como recién instalada.
echo.
choice /c SN /n /m " ¿Continuar? [S/N] "
if errorlevel 2 exit /b 0

docker info >nul 2>&1
if errorlevel 1 (
    echo  Inicie Docker Desktop y vuelva a ejecutar este archivo.
    pause
    exit /b 1
)
echo  Borrando la demo...
docker compose -f docker-compose.yml down -v
call "%~dp0iniciar_demo.bat"
