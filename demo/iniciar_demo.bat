@echo off
setlocal EnableExtensions
chcp 65001 >nul
title BLER ERP - Demo
cd /d "%~dp0"

set "COMPOSE=docker compose -f docker-compose.yml"
set "URL=http://localhost:8069"
set "DB=bler_demo"
set "LOGS=%~dp0logs"
if not exist "%LOGS%" mkdir "%LOGS%"

echo.
echo  ==============================================
echo    BLER ERP - Demo del sistema para talleres
echo  ==============================================
echo.

rem --- 1. Docker instalado y en marcha ---------------------------------------
where docker >nul 2>&1
if errorlevel 1 goto :no_docker

docker info >nul 2>&1
if not errorlevel 1 goto :docker_ok
if not exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" goto :no_docker
echo  Iniciando Docker Desktop (puede tardar un par de minutos)...
start "" "%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
set /a TRIES=0
:wait_docker
ping -n 6 127.0.0.1 >nul
docker info >nul 2>&1
if not errorlevel 1 goto :docker_ok
set /a TRIES+=1
if %TRIES% lss 60 goto :wait_docker
echo.
echo  [ERROR] Docker Desktop no respondió en 5 minutos.
echo  Ábralo desde el menú Inicio, espere a que diga "Engine running"
echo  y vuelva a ejecutar este archivo.
goto :fail

:docker_ok
echo  [OK] Docker está en marcha.

rem --- 2. Si la demo ya está corriendo, solo abrir el navegador --------------
set "RUNNING="
for /f %%i in ('%COMPOSE% ps --status running -q odoo 2^>nul') do set "RUNNING=1"
if defined RUNNING goto :wait_http

rem El puerto 8069 debe estar libre (otra instalación de Odoo lo ocuparía).
netstat -ano | findstr /r /c:":8069 .*LISTENING" >nul
if not errorlevel 1 (
    echo.
    echo  [ERROR] El puerto 8069 ya está en uso por otro programa.
    echo  Cierre la otra instalación de Odoo y vuelva a intentarlo.
    goto :fail
)

rem --- 3. Imagen y base de datos -------------------------------------------
echo  Preparando la aplicación. La primera vez descarga unos 2 GB
echo  y puede tardar entre 5 y 15 minutos según su internet...
%COMPOSE% build odoo > "%LOGS%\01_imagen.log" 2>&1
if errorlevel 1 (
    echo  [ERROR] No se pudo preparar la imagen. Revise su conexión a internet.
    echo  Detalle: %LOGS%\01_imagen.log
    goto :fail
)
%COMPOSE% up -d --wait db > "%LOGS%\02_base.log" 2>&1
if errorlevel 1 (
    echo  [ERROR] No arrancó la base de datos. Detalle: %LOGS%\02_base.log
    goto :fail
)

set "SEEDED="
for /f %%i in ('%COMPOSE% exec -T db psql -U odoo -d %DB% -Atc "select 1 from ir_config_parameter where key='bler_demo.seeded'" 2^>nul') do set "SEEDED=%%i"
if "%SEEDED%"=="1" goto :start_odoo

echo  [OK] Aplicación lista. Creando la base de demostración (unos 2 minutos)...
rem Si quedó una base a medias (instalación interrumpida), se crea de nuevo.
%COMPOSE% exec -T db dropdb -U odoo --if-exists %DB% > "%LOGS%\03_instalacion.log" 2>&1

echo    - Paso 1 de 4: base de datos e idioma español
%COMPOSE% run --rm -T odoo odoo -c /etc/odoo/odoo.conf -d %DB% -i base --load-language=es_419 --stop-after-init --no-http >> "%LOGS%\03_instalacion.log" 2>&1
if errorlevel 1 goto :install_failed

echo    - Paso 2 de 4: empresa de ejemplo en Ecuador
%COMPOSE% run --rm -T odoo odoo shell -c /etc/odoo/odoo.conf -d %DB% --no-http < setup_company.py >> "%LOGS%\03_instalacion.log" 2>&1
if errorlevel 1 goto :install_failed

echo    - Paso 3 de 4: módulos del taller y contabilidad de Ecuador
%COMPOSE% run --rm -T odoo odoo -c /etc/odoo/odoo.conf -d %DB% -i l10n_ec,contacts,bler_taller,bler_branding,muk_web_theme,web_dark_mode --stop-after-init --no-http >> "%LOGS%\03_instalacion.log" 2>&1
if errorlevel 1 goto :install_failed

echo    - Paso 4 de 4: clientes, vehículos y órdenes de ejemplo
%COMPOSE% run --rm -T odoo odoo shell -c /etc/odoo/odoo.conf -d %DB% --no-http < seed_demo.py >> "%LOGS%\03_instalacion.log" 2>&1
if errorlevel 1 goto :install_failed

rem El shell no devuelve error si el script falla: confirmar la marca final.
set "SEEDED="
for /f %%i in ('%COMPOSE% exec -T db psql -U odoo -d %DB% -Atc "select 1 from ir_config_parameter where key='bler_demo.seeded'" 2^>nul') do set "SEEDED=%%i"
if not "%SEEDED%"=="1" goto :install_failed
echo  [OK] Base de demostración creada.

:start_odoo
%COMPOSE% up -d odoo > "%LOGS%\04_arranque.log" 2>&1
if errorlevel 1 (
    echo  [ERROR] No arrancó la aplicación. Detalle: %LOGS%\04_arranque.log
    goto :fail
)

rem --- 4. Esperar a que responda y abrir el navegador -----------------------
:wait_http
echo  Esperando a que BLER ERP responda...
set /a TRIES=0
:wait_http_loop
curl -s -f -o nul "%URL%/web/login" >nul 2>&1
if not errorlevel 1 goto :open
set /a TRIES+=1
if %TRIES% geq 60 (
    echo  [ERROR] BLER ERP no respondió en 3 minutos.
    echo  Pruebe abrir %URL% en el navegador en unos minutos.
    goto :fail
)
ping -n 4 127.0.0.1 >nul
goto :wait_http_loop

:open
start "" "%URL%"
echo.
echo  ==============================================
echo    BLER ERP está listo en %URL%
echo  ==============================================
echo.
echo    Administrador:  usuario admin     contraseña admin
echo    Mecánico:       usuario mecanico  contraseña mecanico
echo.
echo    Puede cerrar esta ventana: la demo sigue funcionando.
echo    Para apagarla, ejecute detener_demo.bat
echo.
pause
exit /b 0

:no_docker
echo  [ERROR] Docker Desktop no está instalado.
echo.
echo  1. Descárguelo desde https://www.docker.com/products/docker-desktop/
echo  2. Instálelo con las opciones por defecto y reinicie la PC.
echo  3. Abra Docker Desktop una vez y acepte los términos.
echo  4. Vuelva a ejecutar este archivo.
echo.
start "" "https://www.docker.com/products/docker-desktop/"
goto :fail

:install_failed
echo.
echo  [ERROR] Falló la creación de la base de demostración.
echo  Detalle: %LOGS%\03_instalacion.log
echo  Puede intentarlo de nuevo ejecutando este archivo otra vez.

:fail
echo.
pause
exit /b 1
