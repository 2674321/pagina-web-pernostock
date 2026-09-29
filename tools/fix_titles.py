#!/usr/bin/env python3
"""Asigna un <title> descriptivo a cada pagina.

Tras la recuperacion, varias paginas quedaron con <title>ERROR</title> y el
resto repetia el mismo texto, lo que es malo para buscadores y para el
historial del navegador.

Uso: python3 tools/fix_titles.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIX = " | PernoStock Ltda.cl"

TITLES = {
    "index.html": "Venta de pernos y elementos de fijación",
    "404.html": "Página no encontrada",
    "ERROR.html": "Error al cargar la página",
    "catalogos.html": "Catálogos y fichas técnicas",
    "certificaciones.html": "Certificaciones",
    "crear_cuenta.html": "Crear una cuenta",
    "fichas_tecnicas.html": "Fichas técnicas",
    "inicio_sesion.html": "Iniciar sesión",
    "lineas_de_negocio.html": "Líneas de negocio",
    "pagina_servicios_principal.html": "Nuestros servicios",
    "politicas_de_la_empresa.html": "Políticas y compromisos",
    "preguntas_frecuentes.html": "Preguntas frecuentes",
    "servicio_de_arriendo.html": "Arriendo de maquinaria",
    "servicio_de_calibracion.html": "Calibración de equipos",
    "servicio_mantenimiento.html": "Mantención y reparación",
    "sobre_calidad.html": "Política de calidad",
    "sobre_la_empresa.html": "Nuestra empresa",
    "sobre_logistica.html": "Logística y distribución",
    "sobre_trazabilidad.html": "Trazabilidad",
    "solicitud_de_certificado_de_calidad.html": "Solicitud de certificado de calidad",
    "sugerencias.html": "Sugerencias y reclamos",
    "ubicaciones.html": "Ubicaciones",
}

DESCRIPTIONS = {
    "index.html": "Pernostock: venta de pernos, tuercas, golillas y elementos de "
                  "fijación para minería, construcción y.context industrial en Chile.",
    "lineas_de_negocio.html": "Atendemos minería, construcción, metalurgia, energía, "
                              "refinería y celulosa con stock permanente.",
    "sobre_logistica.html": "Logística y distribución de Pernostock desde Santiago, "
                            "La Serena y Coquimbo.",
    "politicas_de_la_empresa.html": "Políticas y compromisos de Pernostock.",
    "sobre_la_empresa.html": "Conoce la misión, visión y objetivo de Pernostock.",
    "sobre_calidad.html": "Política de calidad de Pernostock y controles de producción.",
    "sobre_trazabilidad.html": "Trazabilidad de cada lote de producto en Pernostock.",
    "certificaciones.html": "Certificaciones y estándares con los que trabaja Pernostock.",
    "fichas_tecnicas.html": "Fichas técnicas de pernos, tuercas, golillas, cadenas y taladros.",
    "pagina_servicios_principal.html": "Arriendo de maquinaria, calibración de equipos y "
                                       "mantención para la industria.",
    "servicio_de_arriendo.html": "Servicio de arriendo de maquinaria industrial.",
    "servicio_de_calibracion.html": "Servicio de calibración de equipos.",
    "servicio_mantenimiento.html": "Servicio de mantención y reparación.",
    "ubicaciones.html": "Sucursales de Pernostock en Santiago, La Serena y Coquimbo.",
    "inicio_sesion.html": "Inicia sesión en tu cuenta de Pernostock.",
    "crear_cuenta.html": "Crea tu cuenta de Pernostock.",
    "solicitud_de_certificado_de_calidad.html": "Solicita el certificado de calidad de "
                                                "los productos que compraste.",
    "preguntas_frecuentes.html": "Preguntas frecuentes sobre productos y servicios.",
    "sugerencias.html": "Envía sugerencias y reclamos a Pernostock.",
    "ERROR.html": "Ocurrió un error al cargar la página.",
    "404.html": "La página solicitada no existe o fue movida.",
    "catalogos.html": "Descarga el catálogo general y las fichas técnicas de Pernostock.",
}


def main() -> None:
    for name, title in TITLES.items():
        page = ROOT / name
        if not page.exists():
            print(f"  (omitida, no existe) {name}")
            continue

        text = page.read_text(encoding="utf-8")
        new_title = title + SUFFIX

        if re.search(r"<title>.*?</title>", text, re.S):
            text = re.sub(r"<title>.*?</title>", f"<title>{new_title}</title>",
                          text, count=1, flags=re.S)
        else:
            text = text.replace(
                "</title>", "", 1
            ).replace("<head>", f"<head>\n    <title>{new_title}</title>", 1)

        # Anade o actualiza la meta descripcion.
        desc = DESCRIPTIONS.get(name, "")
        if desc:
            desc = desc.replace(" y.context", " y")
            meta = f'    <meta name="description" content="{desc}">'
            if re.search(r'<meta name="description"[^>]*>', text):
                text = re.sub(r'<meta name="description"[^>]*>', meta, text, count=1)
            else:
                text = re.sub(r"(<title>.*?</title>)", r"\1\n" + meta, text,
                              count=1, flags=re.S)

        page.write_text(text, encoding="utf-8")
        print(f"  {name:42} -> {new_title}")


if __name__ == "__main__":
    main()
