# Odoo 18 + dependencias Python del módulo de facturación SRI (Somatech)
FROM odoo:18

USER root
# zeep (SOAP SRI) y cryptography/lxml (firma XAdES) que pide el módulo
RUN pip3 install --no-cache-dir --break-system-packages \
        "zeep>=4.2.0" "cryptography>=41.0.0" "lxml>=4.9.0" "requests>=2.31.0"
USER odoo
