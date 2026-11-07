"""Construye el sitio de Ganadería San Juan en docs/ (lo que publica GitHub Pages).

Uso:  python3 construir.py
Páginas: paginas/<slug>.html (solo el cuerpo) → docs/<slug>/index.html; "inicio" va a la raíz.
Cabecera, pie y estilos son comunes. El hierro es la copia del maestro A en plantilla/ (original en diseno/design_handoff_web_san_juan/hierro/),
sin redibujarlo: solo se le cambia el color del trazo (sepia o hueso, las dos combinaciones permitidas).
Fotos y videos: activos/ → docs/activos/.
"""
import hashlib
import re
import shutil
from pathlib import Path

import markdown

RAIZ = Path(__file__).parent
SALIDA = RAIZ / "docs"
HIERRO_SVG = RAIZ / "plantilla" / "hierro-A-positivo.svg"  # copia del maestro en diseno/design_handoff_web_san_juan/hierro/
VERSION_CSS = hashlib.md5((RAIZ / "plantilla" / "estilos.css").read_bytes()).hexdigest()[:8]
DOMINIO = None  # "ganaderiasanjuan.co" cuando el DNS ya apunte a GitHub Pages

# (slug, texto del menú, título de la pestaña, descripción)
PAGINAS = [
    ("inicio", "Ganadería San Juan", "Ganadería San Juan",
     "Una empresa ganadera familiar en el Magdalena Medio colombiano. Crear valor en la tierra desarrollando su capacidad de generar caja."),
    ("quienes-somos", "Quiénes somos", "Quiénes somos y en qué creemos · Ganadería San Juan",
     "Honrar nuestras raíces. Transformar nuestro futuro. La historia, las convicciones y los principios de Ganadería San Juan."),
    ("fincas", "Nuestras fincas", "Nuestras fincas · Ganadería San Juan",
     "San Juan de Frías y San Juan de Potosí: dos fincas para construir el primer modelo."),
    ("yuwu", "Yuwú", "Yuwú · Ganadería San Juan",
     "218 hectáreas de selva húmeda tropical que decidimos cuidar, junto a San Juan de Frías."),
]


def hierro() -> str:
    """El SVG maestro sin metadatos, con el trazo en currentColor para heredar sepia u hueso."""
    s = re.sub(r"<\?xml.*?\?>|<metadata>.*?</metadata>|<title>.*?</title>", "", HIERRO_SVG.read_text(encoding="utf-8"), flags=re.S)
    s = re.sub(r'\s(width|height|xmlns:c2pa)="[^"]*"', "", s)
    s = s.replace('stroke="#1C1208"', 'stroke="currentColor"').replace('aria-label="Hierro San Juan A positivo"', 'aria-label="San Juan"')
    return s.strip()


HIERRO = hierro()
MARCA = f'{HIERRO}<span>SAN JUAN<small>GANADERÍA</small></span>'


def pagina(slug: str, titulo: str, descripcion: str, cuerpo: str) -> str:
    menu = "".join(
        f'<a href="{"/" if s == "inicio" else f"/{s}/"}"{" aria-current=\"page\"" if s == slug else ""}>{nombre}</a>'
        for s, nombre, _, _ in PAGINAS
    ) + '<a href="/#conversemos">Conversemos</a>'
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:image" content="/activos/fotos/predio-01-agua.jpg">
<link rel="icon" href="/activos/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600&family=Zilla+Slab:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/activos/estilos.css?v={VERSION_CSS}">
</head>
<body>
<header class="nav"><div class="contenedor">
  <a class="marca" href="/" aria-label="Ganadería San Juan, inicio">{MARCA}</a>
  <nav class="enlaces" id="menu">{menu}</nav>
  <button class="menu-boton" type="button" aria-expanded="false" aria-controls="menu">Menú</button>
</div></header>
<main>
{cuerpo}
</main>
<footer class="pie"><div class="contenedor">
  <a class="marca" href="/">{MARCA}</a>
  <p>San Juan de Frías · San Juan de Potosí · Magdalena Medio, Colombia</p>
</div></footer>
<script>
  const nav = document.querySelector('.nav'), boton = document.querySelector('.menu-boton');
  boton.addEventListener('click', () => {{
    const abierto = nav.classList.toggle('abierto');
    boton.setAttribute('aria-expanded', abierto); boton.textContent = abierto ? 'Cerrar' : 'Menú';
  }});
  document.querySelectorAll('#menu a').forEach(a => a.addEventListener('click', () => {{
    nav.classList.remove('abierto'); boton.setAttribute('aria-expanded', false); boton.textContent = 'Menú';
  }}));
</script>
</body>
</html>
"""


def cuerpo_de(slug: str) -> str:
    """paginas/<slug>.html se usa tal cual; paginas/<slug>.md es texto largo (el manifiesto) en Markdown."""
    html_ = RAIZ / "paginas" / f"{slug}.html"
    if html_.exists():
        return html_.read_text(encoding="utf-8")
    texto = markdown.markdown((RAIZ / "paginas" / f"{slug}.md").read_text(encoding="utf-8"), extensions=["extra", "smarty"])
    return f"""<section class="encabezado"><div class="contenedor">
  <p class="etiqueta">Ganadería San Juan</p>
  <h1>Quiénes somos y en qué creemos</h1>
  <p class="lema">Honrar nuestras raíces. Transformar nuestro futuro.</p>
</div></section>
<section class="seccion"><div class="contenedor manifiesto">
{texto}
</div></section>
<section class="seccion oscura"><div class="contenedor">
  <p class="etiqueta">La invitación</p>
  <h2>Buscamos aliados que quieran ayudarnos a construir y demostrar esta visión</h2>
  <a class="boton" href="/#conversemos">Conversemos</a>
</div></section>"""


def construir():
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    shutil.copytree(RAIZ / "activos", SALIDA / "activos")
    shutil.copy(RAIZ / "plantilla" / "estilos.css", SALIDA / "activos" / "estilos.css")
    (SALIDA / "activos" / "favicon.svg").write_text(
        HIERRO.replace("currentColor", "#1C1208").replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
        if 'xmlns="' not in HIERRO else HIERRO.replace("currentColor", "#1C1208"), encoding="utf-8")
    (SALIDA / ".nojekyll").write_text("", encoding="utf-8")
    if DOMINIO:
        (SALIDA / "CNAME").write_text(DOMINIO + "\n", encoding="utf-8")
    for slug, _, titulo, descripcion in PAGINAS:
        cuerpo = cuerpo_de(slug)
        destino = SALIDA / ("" if slug == "inicio" else slug) / "index.html"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(pagina(slug, titulo, descripcion, cuerpo), encoding="utf-8")
    print(f"Listo: {len(PAGINAS)} páginas en docs/")


if __name__ == "__main__":
    construir()
