"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""
import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile.rc",
    version="1.0.0.1",
    company_name="Gyllenhaal Productions Inc.",
    file_description="Gestor de pedidos, facturas y albaranes de la empresa Alimentación Chen",
    internal_name="AlimentacionChen",
    legal_copyright="©Daniel Alonso Lázaro 2023",
    original_filename="GestorAlimentacionChen.exe",
    product_name="Gestor Alimentación Chen",
)
