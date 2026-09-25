# Despliegue de BLER ERP en Google Cloud

Análisis de qué se necesita para publicar BLER ERP en Google Cloud y qué tan
accesible es para un taller pequeño. Precios de lista consultados en
septiembre de 2026, en USD, sin descuentos; los totales son estimaciones
propias, no una cotización de Google.

## Resumen

- BLER ERP cabe en **una sola máquina virtual** (Compute Engine) y se levanta
  con el mismo `docker compose` que se usa en local.
- Costo de servidor: **USD 20–45 al mes** según tamaño y región.
- El stack es liviano: Odoo y Postgres usan ~330 MB de RAM en reposo y la base
  `taller_ec` pesa ~68 MB (medido el 2026-09-25).
- El repo ya contiene todo lo necesario (módulos propios, terceros y la
  localización SRI vendorizada en `odoo_ec_addons/`): desplegar es clonar y
  levantar los contenedores.
- El costo real no es el servidor sino el mantenimiento: respaldos,
  actualizaciones y seguridad.

## Opciones en Google Cloud

| Opción | ¿Sirve? | Motivo |
|---|---|---|
| **VM Compute Engine + Docker Compose** | **Sí, recomendada** | Igual que el entorno local. Simple, barata, fácil de respaldar |
| Cloud Run + Cloud SQL + Cloud Storage | No conviene | Odoo no es "sin estado": necesita filestore persistente, cron siempre encendido y websockets (Cloud Run los corta por timeout, máx. 60 min). Cloud SQL se cobra aparte. Más caro y complejo |
| VM gratuita e2-micro (1 GB) | Solo pruebas | Arranca, pero se queda corta al generar PDFs (wkhtmltopdf) y con varios usuarios |

## Costo mensual estimado (VM + disco + IP fija)

| Tamaño | us-east1 (Carolina del Sur) | southamerica-west1 (Santiago) |
|---|---|---|
| e2-micro (2 vCPU compartidas, 1 GB), nivel gratuito | ~$4 (solo la IP) | No aplica (gratis solo en EE. UU.) |
| **e2-small (2 vCPU compartidas, 2 GB)**: 2–5 usuarios | **~$18–20** | ~$25 |
| **e2-medium (2 vCPU compartidas, 4 GB)**: con margen | **~$30–32** | ~$42 |

Desglose:

- VM: e2-small $12.23; e2-medium $24.46 (EE. UU.), $34.98 (Santiago),
  $38.83 (São Paulo).
- IP externa fija en uso: $0.005/hora ≈ **$3.65/mes** (no la cubre el nivel
  gratuito).
- Disco de 30 GB: $1–3 (estándar o balanceado).
- Respaldos en Cloud Storage: < $1.
- Tráfico de salida de un taller: < $1.
- Dominio: `.com` ~$12/año; `.ec` es más caro.
- Cuenta nueva: **$300 de crédito por 90 días**.
- Nivel gratuito permanente: 1 e2-micro en us-west1, us-central1 o us-east1,
  30 GB de disco estándar y 1 GB de salida al mes.

Latencia desde Ecuador: us-east1 responde bien y es la región más barata;
Santiago da algo menos de latencia pero cuesta ~40% más.

## Pasos para desplegar

1. **Cuenta de Google Cloud** con tarjeta (activa la facturación y el crédito).
2. **VM Debian o Ubuntu** con Docker, IP externa fija, firewall abierto solo
   en 80/443 y SSH por IAP (no abierto a internet).
3. **Dominio** con un registro A a la IP (por ejemplo `erp.bler.ec`).
4. **HTTPS**: agregar Caddy al compose (certificado Let's Encrypt
   automático) y `proxy_mode = True` en `odoo.conf`. El 8069 no se expone
   directo.
5. **Endurecer la configuración** (hoy tiene valores de desarrollo):
   - Cambiar `admin_passwd = admin` (la contraseña maestra permite borrar
     bases).
   - Cambiar la contraseña `odoo/odoo` de Postgres.
   - `list_db = False`.
6. **Respaldos automáticos**: `pg_dump` diario más el filestore
   (`/var/lib/odoo`) a un bucket de Cloud Storage con reglas de retención, y
   snapshots programados del disco. Probar una restauración.
7. **Correo**: Google bloquea el puerto 25. Los recordatorios de
   mantenimiento deben salir por SMTP en el 587 (Gmail/Workspace, Brevo…).
8. **SRI**: funciona igual que en local (firma `.p12` y SOAP al SRI).
   Confirmar la zona horaria `America/Guayaquil` en los usuarios.
9. **URL base**: `web.base.url` al dominio (y `web.base.url.freeze`), luego
   reimprimir las etiquetas QR de los vehículos.

## ¿Conviene para un negocio pequeño?

A favor:

- Acceso desde cualquier lugar; el QR del tablero funciona con datos móviles.
- No depende de que la PC del taller esté encendida.
- Respaldos fuera del local.
- Costo predecible y en dólares.

En contra:

- Alguien debe administrarlo (actualizaciones, revisar respaldos, renovar el
  dominio). Si no hay quien lo haga, ese es el costo real.
- La consola de Google Cloud es compleja para alguien no técnico.
- Sin internet en el taller no se puede usar el sistema.

Alternativas más baratas:

- **VPS simple** (Hetzner, DigitalOcean, Contabo): 4 GB por $5–12/mes, con
  interfaz más sencilla. Para una sola VM sale más barato que Google Cloud.
- **PC del taller + Cloudflare Tunnel**: gratis, da HTTPS y dominio público
  sin abrir puertos, y el QR funciona desde fuera. Depende de la luz, el
  internet del local y la salud de esa PC; los respaldos a la nube serían
  obligatorios.

## Recomendación

Empezar con una **e2-small en us-east1** usando el crédito de $300. Primero la
configuración de seguridad y los respaldos, después abrir el acceso a
clientes. Si la RAM queda corta, se cambia a e2-medium en minutos (apagar la
VM, cambiar el tipo, encender).

Pendiente en el repo para producción: `docker-compose.prod.yml` con Caddy,
`odoo.conf` de producción y un script de respaldo a Cloud Storage.

## Acceso desde la red local (mientras no se despliega)

- Dirección: `http://192.168.100.8:8069` (IP Wi-Fi de la PC del taller;
  escribir `http://` explícito en el teléfono).
- Docker publica el 8069 en todas las interfaces, pero la regla que crea
  Docker Desktop (`com.docker.backend`, solo perfil Público) no bastó: el
  teléfono daba timeout. Se resolvió con una regla explícita, creada desde una
  terminal de administrador:

  ```powershell
  New-NetFirewallRule -DisplayName "BLER ERP (Odoo 8069, red local)" -Direction Inbound -Protocol TCP -LocalPort 8069 -RemoteAddress LocalSubnet -Action Allow -Profile Any
  ```

  Solo acepta dispositivos de la red local y aplica con el Wi-Fi como Público
  o Privado. Se quita con
  `Remove-NetFirewallRule -DisplayName "BLER ERP (Odoo 8069, red local)"`.
- `web.base.url` fijada en `http://192.168.100.8:8069` con
  `web.base.url.freeze = True`. Sin el freeze, Odoo la reescribe a
  `http://localhost:8069` cada vez que un administrador entra desde la PC, y
  los enlaces y QR dejan de abrir en el teléfono.
- El router asigna la IP por DHCP: conviene reservar `192.168.100.8` para esta
  PC. Si cambia, hay que actualizar `web.base.url` y reimprimir las etiquetas.
- Si aun así no abre desde el teléfono, verificar que esté en la misma red
  (no en la de invitados, que suele aislar a los clientes) y que tenga los
  datos móviles apagados.

## Fuentes

- [Precio e2-small – Economize](https://www.economize.cloud/resources/gcp/pricing/compute-engine/e2-small/)
- [Precio e2-medium – CloudPrice](https://cloudprice.net/gcp/compute/instances/e2-medium)
- [e2-medium por región – gcloud-compute.com](https://gcloud-compute.com/e2-medium.html)
- [Nivel gratuito de Google Cloud](https://docs.cloud.google.com/free/docs/free-cloud-features)
- [Precio de IP externa – DoiT](https://www.doit.com/blog/no-more-free-external-ips-on-google-cloud-how-much-will-it-cost-you)
- [Precios de red VPC – Google](https://cloud.google.com/vpc/network-pricing)
- [Precios de Cloud SQL – Bytebase](https://www.bytebase.com/dbcost/cloudsql-pricing/)
- [WebSockets en Cloud Run – Google](https://docs.cloud.google.com/run/docs/triggering/websockets)
- [Despliegue de Odoo 18 – documentación oficial](https://www.odoo.com/documentation/18.0/administration/on_premise/deploy.html)
