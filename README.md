# PernoStock — sitio web



<p align="center"><img src="docs/branding/app-icon.svg" width="150" alt="PernoStock Web"></p>

<p align="center"><img src="docs/branding/hero-banner.svg" width="100%" alt="PernoStock Web"></p>

**Autor:** [Patricio Varela C.](https://github.com/2674321) · **ORCID:** [0009-0002-1087-9445](https://orcid.org/0009-0002-1087-9445) · **Citación:** [CITATION.cff](CITATION.cff)

> **Archivo personal, no es un proyecto en curso.**
> Este fue mi primer sitio web, hecho en unos 7 días a los 18 años (2023–2024),
> para la empresa en la que trabajaba. Se conserva tal cual, como recuerdo, y no
> está pensado para seguir desarrollándose ni para publicarse.

Sitio corporativo de **PernoStock Ltda.**, empresa chilena de venta de pernos,
tuercas, golillas y elementos de fijación, con servicios de arriendo de
maquinaria, calibración y mantención.

El sitio es **HTML, CSS y JavaScript estáticos**: no necesita PHP, base de datos
ni proceso de compilación. Se sube tal cual al hosting.

---

## Cómo abrirlo

No hace falta instalar nada. Solo Python 3:

```bash
python3 tools/serve.py
```

Y abrir <http://localhost:8000>. Para usar otro puerto:

```bash
python3 tools/serve.py 8080
```

También funciona con cualquier otro servidor estático, por ejemplo:

```bash
python3 -m http.server 8000
```

> Antes funcionaba con XAMPP. Ya no es necesario: el sitio no tiene PHP.

---

## Estructura

```
.
├── index.html                  Página de inicio
├── catalogos.html              Catálogos y fichas
├── <resto de páginas>.html      22 páginas en total
├── 404.html                    Página de error
├── ERROR.html                  Plantilla de error original
├── css/archivos/               Una hoja de estilos por página
├── images/                     Imágenes del sitio
├── js/                         JavaScript por página + javascript.js común
├── media/pdf/fichas-tecnicas/  Fichas técnicas en PDF y ZIP
├── assets/                     favicon-256.png
├── .htaccess                   Configuración de Apache (404, caché, compresión)
└── tools/                      Scripts de desarrollo y verificación
```

---

## Verificar que todo esté bien

```bash
# 1. Revisa que no haya enlaces ni imágenes rotas
python3 tools/check_links.py

# 2. Abre cada página en Chromium y detecta errores de JavaScript
#    (requiere el servidor levantado en otra terminal)
pip install playwright && playwright install chromium
python3 tools/serve.py &
python3 tools/browser_check.py
```

`browser_check.py` recorre las 22 páginas y reporta errores de JS, peticiones
fallidas y páginas vacías. Actualmente las 22 pasan sin errores.

---

## Publicar en GitHub

El repositorio no tiene historial ni remoto todavía. Para crearlo:

```bash
cd /ruta/a/este/proyecto
git init
git add .
git commit -m "Sitio PernoStock: sitio estatico recuperado y verificado"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```

### Nota sobre el tamaño

El repositorio pesa alrededor de **180 MB**, casi todo en
`media/pdf/fichas-tecnicas/` (165 MB de fichas en PDF más un ZIP de 30 MB).
Ningún archivo supera los 100 MB, así que GitHub lo acepta sin usar Git LFS.

Si prefieres un clon más liviano, activa [Git LFS](https://git-lfs.com) para los
PDF antes del primer commit:

```bash
git lfs install
git lfs track "*.pdf" "*.zip"
git add .gitattributes && git commit -m "Activar Git LFS para fichas tecnicas"
```

---

## Desplegar en el hosting

El hosting usa DirectAdmin por FTP. Se sube **el contenido de la raíz del
proyecto**, es decir el `.html`, `css/`, `images/`, `js/`, `media/`, `assets/` y
`.htaccess`.

Con `lftp`:

```bash
lftp -u USUARIO,CONTRASENA ftp.absa.cl <<'EOF'
mirror -R --verbose --delete images css js media assets *.html .htaccess
bye
EOF
```

El DNS tarda hasta 4 horas en propagarse tras el cambio.

> Las credenciales de FTP y del panel **no** están en este repositorio. Se
> guardan fuera del control de versiones y `.gitignore` bloquea cualquier
> archivo que parezca contenerlas.

---

## Estado del proyecto al archivarlo

No son errores: es simplemente cómo quedó. Se documenta para que quede claro que
**nada de esto está roto por descuido**.

### reCAPTCHA nunca estuvo activo

Las 11 páginas con formulario de contacto tienen:

```html
<div class="g-recaptcha" data-sitekey="pagina pernostock"></div>
```

`pagina pernostock` es texto de relleno, no una clave válida de Google
reCAPTCHA. El `<div>` simplemente se dibuja vacío y **el envío del formulario no
se bloquea**: los formularios mandaban datos, sin captcha. Se dejó así.

### Los formularios dependían del servidor real

Apuntan a `/pub/casos-forms/formulario.php`, un endpoint PHP que vive en el
hosting y nunca estuvo en el repositorio. Al trabajar siempre sobre el servidor
real de la empresa —que era también el de pruebas— no hubo nunca un entorno
separado donde probar el envío: se subía y se veía si funcionaba.

Por eso el enlace a las fichas que apuntaba a `http://localhost/`: funcionaba en
la máquina donde se programaba y en ningún otro lado.

### Dos páginas quedaron en construcción

`preguntas_frecuentes.html` y `sugerencias.html` muestran un aviso de "en
construcción". Es el estado en que se dejó.

### El catálogo general vive en el servidor

El botón "Descarga nuestro Catálogo" y dos fichas apuntan a
`https://pernostock.cl/...` porque esos archivos no están en el repositorio.
Uno de ellos, `nueva-ficha-tecnica-golilla-reparticion.pdf`, falta desde antes:
hay un `aviso.txt` en `media/pdf/fichas-tecnicas/` que lo explica.

### Los CSS están duplicados

Cada página carga su propia hoja de estilos en `css/archivos/`, y casi todas son
copias del mismo bloque de ~7 KB con pequeñas diferencias. Funciona, pero
cambiar un estilo exige editar varios archivos. Extrayendo un `css/base.css`
común se arreglaría.

---

## Scripts de `tools/`

| Script | Para qué sirve |
|---|---|
| `serve.py` | Servidor local con soporte de `404.html` |
| `check_links.py` | Detecta enlaces, imágenes y `url()` de CSS rotos |
| `browser_check.py` | Recorre todas las páginas en Chromium y reporta errores |
| `optimize_images.py` | Reduce el peso de las imágenes (`--dry` para simular) |
| `fix_references.py` | Normaliza rutas de JS y URLs de Bootstrap |
| `fix_fichas_links.py` | Apunta las fichas técnicas a los PDF locales |
| `fix_titles.py` | Asigna un `<title>` y `description` por página |
| `make_favicon.py` | Genera `favicon.ico` desde el logo |

---

## Agradecimientos

Miembros de ASTM y RCSC. Marcas con las que se trabaja: Nelson, Skidmore,
Unity, Tone, KFP, RNK y URRREA.

---

## Origen de este repositorio

El proyecto se recuperó de una carpeta de trabajo en XAMPP (`htdocs/`) que
llevaba años sin tocarse. Al recuperarla el sitio **no funcionaba**: no había
página de inicio, las rutas de JavaScript apuntaban a carpetas que ya no
existían y Bootstrap se cargaba desde dos CDNs dados de baja.

El commit inicial de este repositorio es esa puesta en orden: se apartó el
stack de XAMPP, se reunieron los archivos en la raíz, se repararon las rutas y
se construyó la página de inicio que faltaba. **El diseño y los contenidos son
los originales de 2023–2024**; lo único nuevo son la portada y la página de
catálogos.

Lo que **no** se conservó, por no formar parte del sitio:

| Descartado | Motivo |
|---|---|
| `dashboard/`, `xampp/`, `webalizer/` | Boilerplate de XAMPP |
| `htdocs/index.php`, `bitnami.css` | Archivos por defecto de XAMPP |
| `notes/` con datos del hosting | Contenía la contraseña de FTP y del panel, en texto plano. **Esa contraseña se rotó.** |
| `recursos_datos/` (852 KB) | Restos de la web anterior a Pernostock |
| `pagina en construccion/` | Su contenido se integró en la raíz |

> Una copia del material descartado quedó en `/tmp` durante la recuperación, y
> se perdió al limpiarse esa carpeta. Nada de lo listado ahí afectaba al sitio,
> pero sí significa que **el estado previo a la recuperación ya no existe**. Lo
> que hay aquí es el sitio funcionando.
