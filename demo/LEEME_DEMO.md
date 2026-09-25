# BLER ERP: demo para probar en su computadora

Esta carpeta instala una versión de prueba de BLER ERP en su PC con Windows,
con datos de ejemplo de un taller: clientes, vehículos, órdenes de trabajo y
una factura. Los datos son ficticios y todo queda solo en su computadora.

## Requisitos

- Windows 10 u 11 (64 bits) con la virtualización activada (viene activada
  en la mayoría de las PC; si Docker la pide, se activa en la BIOS/UEFI).
- 8 GB de RAM y unos 5 GB libres en disco.
- Conexión a internet la primera vez (descarga unos 2 GB).
- **Docker Desktop**: gratis para uso personal y empresas pequeñas.
  1. Descárguelo desde https://www.docker.com/products/docker-desktop/
  2. Instálelo con las opciones por defecto y reinicie la PC.
  3. Ábralo una vez y acepte los términos (no hace falta crear una cuenta).

## Uso

| Archivo | Qué hace |
|---|---|
| `iniciar_demo.bat` | Arranca la demo y abre el navegador en http://localhost:8069. La primera vez tarda entre 5 y 15 minutos (descarga e instalación); después, menos de un minuto |
| `detener_demo.bat` | Apaga la demo. Los datos se conservan |
| `reiniciar_demo.bat` | Borra todo y deja la demo como recién instalada |

Doble clic en `iniciar_demo.bat`. Si Docker Desktop está cerrado, el script
lo abre y espera a que esté listo.

## Usuarios

| Usuario | Contraseña | Qué ve |
|---|---|---|
| `admin` | `admin` | Todo el sistema: tablero, ventas, facturación, inventario, ajustes |
| `mecanico` | `mecanico` | Lo del día a día del taller: órdenes de trabajo, vehículos, catálogo |

## Qué probar

- **Tablero del taller**: trabajos del día, pendientes y vehículos con
  mantenimiento próximo o vencido.
- **Vehículos**: cada placa con su historial. El Chevrolet Aveo `PCA-1234`
  tiene dos visitas y una factura; el Kia `PDF-9012` tiene el mantenimiento
  vencido.
- **Órdenes de trabajo**: una en reparación (Toyota Hilux de la flota
  Transportes Andinos), una cita confirmada para mañana y un presupuesto en
  borrador (Hyundai Accent).
- **Agenda**: el calendario de trabajos por mecánico.
- **Orden de trabajo en PDF** y **ficha del vehículo en PDF**.
- **Etiqueta QR** del vehículo (botón en la ficha). En la demo el enlace solo
  abre en esta misma PC.
- **Facturación**: de la orden a la cotización y a la factura, con IVA 15% y
  el plan de cuentas de Ecuador.

La facturación electrónica con el SRI no está activa en la demo: necesita la
firma electrónica (.p12) del negocio y se configura al contratar el servicio.

## Si algo falla

- Los detalles de cada paso quedan en la carpeta `logs\`.
- "El puerto 8069 ya está en uso": hay otra instalación de Odoo en marcha;
  ciérrela y vuelva a intentarlo.
- Si la instalación se interrumpió (se cortó internet, se apagó la PC), basta
  con volver a ejecutar `iniciar_demo.bat`: rehace la base desde cero.
- Para desinstalar: `reiniciar_demo.bat` → responder S, cerrar la ventana
  cuando termine, y desinstalar Docker Desktop desde Configuración de Windows.

---

Notas técnicas (para quien mantiene la demo):

- Proyecto de Compose `bler_demo` (volúmenes `bler_demo_demo_db` y
  `bler_demo_demo_data`), independiente de `odoo_stack/`. Solo escucha en
  `127.0.0.1:8069`, no queda abierta a la red.
- Base `bler_demo`: `setup_company.py` deja la empresa en Ecuador/USD antes de
  instalar Contabilidad (así se carga el plan `l10n_ec`), luego se instalan
  los módulos y `seed_demo.py` crea los datos. Al terminar guarda
  `bler_demo.seeded` en `ir.config_parameter`; sin esa marca, el `.bat`
  rehace la base.
- No incluye `l10n_ec_base`/`l10n_ec_edi` (SRI) a propósito.
- Los `.bat` deben tener saltos de línea CRLF (`.gitattributes`: `*.bat -text`).
