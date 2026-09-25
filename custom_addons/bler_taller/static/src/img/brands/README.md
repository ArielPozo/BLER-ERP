# Logos de marcas de vehículos

Logos a color para marcas comunes en Ecuador que no trae el módulo Flota
(Great Wall, Chery, JAC, Changan, Hino...). Se usan como imagen de la marca
(`fleet.vehicle.model.brand.image_128`) solo cuando la marca no tiene una.

- Origen: miniaturas de <https://github.com/filippofilip95/car-logos-dataset>
  (carpeta `logos/thumb`, commit bb2d661), que a su vez las toma de
  carlogos.org, la misma fuente que usa CarCare.
- El dataset tiene licencia MIT, pero **cada logo es marca registrada de su
  fabricante**. Aquí se usan solo para identificar la marca del vehículo que
  se atiende, igual que los logos que trae Flota.
- El nombre del archivo es el nombre de la marca en minúsculas con guiones
  (`great-wall.png`). Los alias (p. ej. "BAIC" -> `baic-motor`) están en
  `models/fleet_vehicle_model_brand.py`.
