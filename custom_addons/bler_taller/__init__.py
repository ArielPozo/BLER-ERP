# -*- coding: utf-8 -*-
from . import models
from . import controllers


def _post_init_hook(env):
    # Marcas comunes en Ecuador que no trae Flota y logos para las que no
    # tienen imagen.
    env["fleet.vehicle.model.brand"]._load_extra_brands()
