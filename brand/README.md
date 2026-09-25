# Marca BLER ERP

**BLER** es la versión hispanizada de *Blair*, por *La bruja de Blair*. El logo une esa idea de magia con el mundo empresarial, en un estilo corporativo, minimalista y de cristal con degradados.

## Concepto

| Elemento | Significado |
|---|---|
| Gema hexagonal facetada | Cristal o bola de cristal: lo mágico. El hexágono también es solidez y estructura (un ERP bien armado) |
| Tres barras ascendentes | Crecimiento, reportes y gestión: lo empresarial |
| Chispa de cuatro puntas sobre la barra más alta | El "toque de magia" que hace crecer el negocio |
| Degradado índigo → violeta → cian | De la noche del bosque a la claridad del cristal |

Lema: **Gestión con un toque de magia**.

## Archivos

| Archivo | Uso |
|---|---|
| `bler_icon.svg` | Ícono solo: favicon, app, avatar |
| `bler_logo_horizontal.svg` | Logo completo sobre fondo claro |
| `bler_logo_horizontal_dark.svg` | Logo completo sobre fondo oscuro |
| `bler_logo_vertical_dark.svg` | Ícono sobre "BLER ERP", sin lema, para fondo oscuro y espacios angostos (barra lateral de MuK) |
| `png/bler_icon_{32,64,180,192,512}.png` | Favicon, ícono iOS (180) y PWA (192/512) |
| `png/bler_logo_horizontal*.png` | Logo en 1640×512, fondo transparente |
| `preview.html` | Hoja de muestra (abrir en el navegador) |

El módulo `bler_branding` usa copias de estos archivos en `static/src/img/` (`favicon.ico` de 16/32/48/64, `bler_icon_{192,512,ios}.png`, `bler_logo.png`/`.svg`, `bler_logo_sidebar.png` = `png/bler_logo_vertical_dark.png`) y `static/description/icon.png`. Si cambia el logo, vuelve a copiarlos conservando los nombres.

## Paleta

| Color | Hex |
|---|---|
| Índigo noche | `#1E1B4B` |
| Violeta hechizo | `#6D28D9` |
| Amatista | `#8B5CF6` |
| Cian cristal | `#22D3EE` |

## Tipografía

Montserrat (800 para "BLER", 300 para "ERP", 500 para el lema). Si no está instalada, los SVG usan Segoe UI o Arial. Los anchos están fijados con `textLength`, así que la composición no se descuadra. Para imprenta, convierte el texto a trazos en Inkscape o Illustrator.

## Exportar PNG de nuevo

No hace falta instalar nada: los PNG se generaron con Edge en modo headless (`msedge --headless=new --screenshot`) sobre una página que muestra el SVG al tamaño deseado, con fondo transparente (`--default-background-color=00000000`).
