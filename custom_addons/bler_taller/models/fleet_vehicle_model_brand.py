# -*- coding: utf-8 -*-
import base64
import re
import unicodedata

from odoo import api, fields, models
from odoo.tools import file_open

LIB_PATH = "bler_taller/static/lib/car-makes-icons/svgs/%s.svg"
LOGO_PATH = "bler_taller/static/src/img/brands/%s.png"

# Íconos de la librería car-makes-icons (static/lib/car-makes-icons).
CAR_MAKE_ICONS = {
    "acura", "alfa-romeo", "am-general", "aston-martin", "audi", "bentley", "bmw",
    "bugatti", "buick", "cadillac", "chevrolet", "chrysler", "daewoo", "dodge", "eagle",
    "ferrari", "fiat", "fisker", "ford", "genesis", "geo", "gmc", "honda", "hummer",
    "hyundai", "infiniti", "isuzu", "jaguar", "jeep", "kia", "lamborghini", "land-rover",
    "lexus", "lincoln", "lotus", "maserati", "maybach", "mazda", "mclaren",
    "mercedes-benz", "mercury", "mini", "mitsubishi", "nissan", "oldsmobile", "panoz",
    "plymouth", "pontiac", "porsche", "ram", "rolls-royce", "saab", "saturn", "scion",
    "smart", "spyker", "subaru", "suzuki", "tesla", "toyota", "volkswagen", "volvo",
}

# Marcas con logo a color en static/src/img/brands (car-logos-dataset): las
# comunes en Ecuador que no trae Flota. Nombre para mostrar -> archivo.
EXTRA_BRANDS = {
    "BAIC": "baic-motor", "Brilliance": "brilliance", "Changan": "changan",
    "Chery": "chery", "Cupra": "cupra", "Dacia": "dacia", "Daihatsu": "daihatsu",
    "Datsun": "datsun", "Dongfeng": "dongfeng", "DS": "ds", "Exeed": "exeed",
    "FAW": "faw", "Foton": "foton", "Freightliner": "freightliner", "GAC": "gac-group",
    "Geely": "geely", "Genesis": "genesis", "GMC": "gmc", "Golden Dragon": "golden-dragon",
    "Great Wall": "great-wall", "Haima": "haima", "Haval": "haval", "Higer": "higer",
    "Hino": "hino", "Hongqi": "hongqi", "Hummer": "hummer", "International": "international",
    "Iveco": "iveco", "JAC": "jac", "Jetour": "jetour", "Jetta": "jetta", "JMC": "jmc",
    "Kenworth": "kenworth", "King Long": "king-long", "Lada": "lada",
    "Leapmotor": "leapmotor", "Lifan": "lifan", "Lynk & Co": "lynk-and-co", "Mack": "mack",
    "Mahindra": "mahindra", "MAN": "man", "Maxus": "maxus", "Omoda": "omoda",
    "Proton": "proton", "Ram": "ram", "Scania": "scania", "SEAT": "seat",
    "Shacman": "shacman", "Sinotruk": "sinotruk", "Soueast": "soueast",
    "SsangYong": "ssangyong", "Tata": "tata", "Wey": "wey", "Wuling": "wuling",
    "Yutong": "yutong", "Zeekr": "zeekr", "Zotye": "zotye",
}
LOGO_FILES = set(EXTRA_BRANDS.values()) | {"kia"}

# Nombres de marca frecuentes que no coinciden con el nombre del archivo.
CAR_MAKE_ALIASES = {
    "alfa": "alfa-romeo",
    "mercedes": "mercedes-benz",
    "benz": "mercedes-benz",
    "tesla-motors": "tesla",
    "vw": "volkswagen",
    "chevy": "chevrolet",
    "gm": "gmc",
    "range-rover": "land-rover",
    "baic": "baic-motor",
    "baic-motor": "baic-motor",
    "gac": "gac-group",
    "gwm": "great-wall",
    "greatwall": "great-wall",
    "great-wall-motors": "great-wall",
    "dfsk": "dongfeng",
    "dongfeng-sokon": "dongfeng",
    "ssang-yong": "ssangyong",
    "kgm": "ssangyong",
    "lynk-co": "lynk-and-co",
}


def car_make_slug(name):
    """'Rolls-Royce' -> 'rolls-royce', 'Citroën' -> 'citroen', 'Lynk & Co' -> 'lynk-and-co'."""
    name = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    name = re.sub(r"[^a-z0-9]+", " ", name.lower().replace("&", " and "))
    slug = "-".join(name.split())
    return CAR_MAKE_ALIASES.get(slug, slug)


def car_make_icon(name):
    slug = car_make_slug(name)
    return slug if slug in CAR_MAKE_ICONS else False


class FleetVehicleModelBrand(models.Model):
    _inherit = "fleet.vehicle.model.brand"

    icon_class = fields.Char(
        string="Ícono", compute="_compute_icon_class",
        help="Clase CSS del ícono de la marca (librería car-makes-icons).",
    )
    logo_url = fields.Char(string="URL del logo", compute="_compute_logo_url")

    @api.depends("name")
    def _compute_icon_class(self):
        for brand in self:
            icon = car_make_icon(brand.name)
            brand.icon_class = "car-%s" % icon if icon else False

    @api.depends("image_128")
    def _compute_logo_url(self):
        # bin_size: solo interesa si hay imagen, sin leer el archivo.
        for brand, sized in zip(self, self.with_context(bin_size=True)):
            if brand.id and sized.image_128:
                unique = int(brand.write_date.timestamp()) if brand.write_date else 0
                brand.logo_url = "/web/image/fleet.vehicle.model.brand/%s/image_128?unique=%s" % (brand.id, unique)
            else:
                brand.logo_url = False

    @api.model_create_multi
    def create(self, vals_list):
        brands = super().create(vals_list)
        brands._set_default_logo()
        return brands

    def write(self, vals):
        res = super().write(vals)
        if "name" in vals or "image_128" in vals:
            self._set_default_logo()
        return res

    @api.model
    def _default_logo_data(self, name):
        """Logo por defecto: primero el PNG a color, si no el SVG de car-makes-icons."""
        slug = car_make_slug(name)
        if slug in LOGO_FILES:
            path = LOGO_PATH % slug
        elif slug in CAR_MAKE_ICONS:
            path = LIB_PATH % slug
        else:
            return False
        with file_open(path, "rb") as f:
            return base64.b64encode(f.read())

    def _set_default_logo(self):
        """Pone el logo por defecto a las marcas que no tienen imagen.

        sudo: los adjuntos SVG solo los guarda con su tipo real un
        administrador; el archivo sale del propio módulo.
        """
        for brand in self.filtered(lambda b: not b.image_128):
            data = self._default_logo_data(brand.name)
            if data:
                brand.sudo().image_128 = data

    @api.model
    def _load_extra_brands(self):
        """Crea las marcas de EXTRA_BRANDS que falten y completa logos vacíos.

        Se busca por nombre normalizado para no duplicar marcas que el
        usuario ya creó con otra escritura ("Great wall", "GWM"...).
        """
        brands = self.with_context(active_test=False).search([])
        existing = {car_make_slug(b.name) for b in brands}
        to_create = [{"name": name} for name, slug in EXTRA_BRANDS.items() if slug not in existing]
        brands._set_default_logo()
        return self.create(to_create)
