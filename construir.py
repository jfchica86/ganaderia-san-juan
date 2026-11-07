"""Construye el sitio de Ganadería San Juan en docs/ (lo que publica GitHub Pages), en español y en inglés.

Uso:  python3 construir.py
Páginas: paginas/<slug>.html (solo el cuerpo) o paginas/<slug>.md (texto largo) → docs/<slug>/index.html;
"inicio" va a la raíz. El inglés vive en paginas/en/ con los mismos nombres y sale en /en/.
En las páginas los enlaces se escriben siempre como en español ("/fincas/", "/#conversemos"); al
construir el inglés se les antepone /en/. Las rutas a /activos/ se quedan igual en los dos idiomas.
Cabecera, pie y estilos son comunes. El hierro es la copia del maestro A en plantilla/ (original en
diseno/design_handoff_web_san_juan/hierro/), sin redibujarlo: solo se le cambia el color del trazo
(sepia o hueso, las dos combinaciones permitidas). Fotos y videos: activos/ → docs/activos/.
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
# Sin dominio propio el sitio vive en jfchica86.github.io/ganaderia-san-juan/: todas las rutas llevan ese prefijo
BASE = "/" if DOMINIO else "/ganaderia-san-juan/"

SLUGS = ["inicio", "quienes-somos", "fincas", "yuwu"]

IDIOMAS = {
    "es": {
        "carpeta": "", "otro": "en", "boton": "EN", "boton_nombre": "English",
        "menu": ["Ganadería San Juan", "Quiénes somos", "Nuestras fincas", "Yuwú"], "conversemos": "Conversemos",
        "titulos": ["Ganadería San Juan", "Quiénes somos y en qué creemos · Ganadería San Juan",
                    "Nuestras fincas · Ganadería San Juan", "Yuwú · Ganadería San Juan"],
        "descripciones": [
            "Una empresa ganadera familiar en el Magdalena Medio colombiano. Crear valor en la tierra desarrollando su capacidad de generar caja.",
            "Honrar nuestras raíces. Transformar nuestro futuro. La historia, las convicciones y los principios de Ganadería San Juan.",
            "San Juan de Frías y San Juan de Potosí: dos fincas para construir el primer modelo.",
            "218 hectáreas de selva húmeda tropical que decidimos cuidar, junto a San Juan de Frías.",
        ],
        "abrir": "Menú", "cerrar": "Cerrar", "inicio_aria": "Ganadería San Juan, inicio",
        "pie": "San Juan de Frías · San Juan de Potosí · Magdalena Medio, Colombia",
        "manifiesto": ("Quiénes somos y en qué creemos", "Honrar nuestras raíces. Transformar nuestro futuro.",
                       "La invitación", "Buscamos aliados que quieran ayudarnos a construir y demostrar esta visión"),
    },
    "en": {
        "carpeta": "en/", "otro": "es", "boton": "ES", "boton_nombre": "Español",
        "menu": ["Ganadería San Juan", "Who we are", "Our farms", "Yuwú"], "conversemos": "Let's talk",
        "titulos": ["Ganadería San Juan", "Who we are and what we believe · Ganadería San Juan",
                    "Our farms · Ganadería San Juan", "Yuwú · Ganadería San Juan"],
        "descripciones": [
            "A family cattle company in Colombia's Magdalena Medio. Creating value in the land by developing its capacity to generate cash.",
            "Honor our roots. Transform our future. The story, convictions and principles of Ganadería San Juan.",
            "San Juan de Frías and San Juan de Potosí: two farms to build the first model.",
            "218 hectares of tropical rainforest we chose to protect, next to San Juan de Frías.",
        ],
        "abrir": "Menu", "cerrar": "Close", "inicio_aria": "Ganadería San Juan, home",
        "pie": "San Juan de Frías · San Juan de Potosí · Magdalena Medio, Colombia",
        "manifiesto": ("Who we are and what we believe", "Honor our roots. Transform our future.",
                       "The invitation", "We are looking for partners who want to help us build and prove this vision"),
    },
}


def hierro() -> str:
    """El SVG maestro sin metadatos, con el trazo en currentColor para heredar sepia u hueso."""
    s = re.sub(r"<\?xml.*?\?>|<metadata>.*?</metadata>|<title>.*?</title>", "", HIERRO_SVG.read_text(encoding="utf-8"), flags=re.S)
    s = re.sub(r'\s(width|height|xmlns:c2pa)="[^"]*"', "", s)
    s = s.replace('stroke="#1C1208"', 'stroke="currentColor"').replace('aria-label="Hierro San Juan A positivo"', 'aria-label="San Juan"')
    return s.strip()


HIERRO = hierro()
# El sello como en la presentación: hierro + «San Juan» en Jost, y debajo una regla con «Ganadería»
SELLO_HIERRO = re.sub(r'viewBox="[^"]*"', 'viewBox="18 8 64 82"', HIERRO, count=1)
MARCA = (f'<span class="fila">{SELLO_HIERRO}<span class="nombre">San Juan</span></span>'
         '<span class="fila2"><i></i><span class="sub">Ganadería</span></span>')


def ruta(slug: str) -> str:
    return "" if slug == "inicio" else f"{slug}/"


def pagina(lang: str, slug: str, cuerpo: str) -> str:
    t, i = IDIOMAS[lang], SLUGS.index(slug)
    otro = IDIOMAS[t["otro"]]
    menu = "".join(
        f'<a href="/{ruta(s)}"{" aria-current=\"page\"" if s == slug else ""}>{nombre}</a>'
        for s, nombre in zip(SLUGS, t["menu"])
    ) + f'<a href="/#conversemos">{t["conversemos"]}</a>'
    aqui = f"https://{DOMINIO}/" if DOMINIO else "https://jfchica86.github.io/ganaderia-san-juan/"
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t["titulos"][i]}</title>
<meta name="description" content="{t["descripciones"][i]}">
<meta property="og:title" content="{t["titulos"][i]}">
<meta property="og:description" content="{t["descripciones"][i]}">
<meta property="og:image" content="/activos/fotos/predio-01-agua.jpg">
<link rel="alternate" hreflang="{lang}" href="{aqui}{t["carpeta"]}{ruta(slug)}">
<link rel="alternate" hreflang="{t["otro"]}" href="{aqui}{otro["carpeta"]}{ruta(slug)}">
<link rel="icon" href="/activos/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500&family=Work+Sans:wght@400;500;600&family=Zilla+Slab:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/activos/estilos.css?v={VERSION_CSS}">
</head>
<body>
<header class="nav"><div class="contenedor">
  <a class="marca" href="/" aria-label="{t["inicio_aria"]}">{MARCA}</a>
  <nav class="enlaces" id="menu">{menu}</nav>
  <div class="nav-derecha">
    <a class="idioma" href="@@OTRO@@{ruta(slug)}" hreflang="{t["otro"]}" lang="{t["otro"]}" title="{t["boton_nombre"]}">{t["boton"]}</a>
    <button class="menu-boton" type="button" aria-expanded="false" aria-controls="menu">{t["abrir"]}</button>
  </div>
</div></header>
<main>
{cuerpo}
</main>
<footer class="pie"><div class="contenedor">
  <a class="marca" href="/">{MARCA}</a>
  <p>{t["pie"]}</p>
</div></footer>
<script>
  const nav = document.querySelector('.nav'), boton = document.querySelector('.menu-boton');
  boton.addEventListener('click', () => {{
    const abierto = nav.classList.toggle('abierto');
    boton.setAttribute('aria-expanded', abierto); boton.textContent = abierto ? '{t["cerrar"]}' : '{t["abrir"]}';
  }});
  document.querySelectorAll('#menu a').forEach(a => a.addEventListener('click', () => {{
    nav.classList.remove('abierto'); boton.setAttribute('aria-expanded', false); boton.textContent = '{t["abrir"]}';
  }}));
</script>
</body>
</html>
"""


def cuerpo_de(lang: str, slug: str) -> str:
    """paginas/[en/]<slug>.html se usa tal cual; .md es texto largo (el manifiesto) en Markdown."""
    carpeta = RAIZ / "paginas" / IDIOMAS[lang]["carpeta"]
    html_ = carpeta / f"{slug}.html"
    if html_.exists():
        return html_.read_text(encoding="utf-8")
    texto = markdown.markdown((carpeta / f"{slug}.md").read_text(encoding="utf-8"), extensions=["extra", "smarty"])
    titulo, lema, etiqueta, invitacion = IDIOMAS[lang]["manifiesto"]
    return f"""<section class="encabezado"><div class="contenedor">
  <p class="etiqueta">Ganadería San Juan</p>
  <h1>{titulo}</h1>
  <p class="lema">{lema}</p>
</div></section>
<section class="seccion"><div class="contenedor manifiesto">
{texto}
</div></section>
<section class="seccion oscura"><div class="contenedor">
  <p class="etiqueta">{etiqueta}</p>
  <h2>{invitacion}</h2>
  <a class="boton" href="/#conversemos">{IDIOMAS[lang]["conversemos"]}</a>
</div></section>"""


def rutas_finales(html_: str, lang: str) -> str:
    """Antepone /en/ a los enlaces entre páginas del inglés, y después el prefijo del sitio a todo."""
    carpeta, otra = IDIOMAS[lang]["carpeta"], IDIOMAS[IDIOMAS[lang]["otro"]]["carpeta"]
    if carpeta:
        html_ = re.sub(r'href="/(?!/|activos/|@@)', f'href="/{carpeta}', html_)
    html_ = html_.replace('href="@@OTRO@@', f'href="/{otra}')
    html_ = re.sub(r'((?:href|src)=")/(?!/)', rf"\g<1>{BASE}", html_)
    return html_.replace('content="/activos/', f'content="{BASE}activos/')


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
    for lang, t in IDIOMAS.items():
        for slug in SLUGS:
            destino = SALIDA / t["carpeta"] / ruta(slug) / "index.html"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(rutas_finales(pagina(lang, slug, cuerpo_de(lang, slug)), lang), encoding="utf-8")
    print(f"Listo: {len(SLUGS)} páginas en español y {len(SLUGS)} en inglés, en docs/")


if __name__ == "__main__":
    construir()
