# PernoStock — sitio web

Sitio corporativo de **PernoStock Ltda.**, empresa chilena de venta de pernos,
tuercas, golillas y elementos de fijación, con servicios de arriendo de
maquinaria, calibración y mantención.

El sitio es **HTML, CSS y JavaScript estáticos**: no necesita PHP, base de datos
ni proceso de compilación. Se sube tal cual al hosting.

---

## Cómo probarlo en local

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

## Problemas conocidos

Estas cosas requieren una decisión o una clave que no se puede inventar desde
el código:

### 1. La clave de reCAPTCHA es un placeholder

Las 11 páginas con formulario de contacto tienen:

```html
<div class="g-recaptcha" data-sitekey="pagina pernostock"></div>
```

`pagina pernostock` no es una clave válida de Google reCAPTCHA, por lo que el
widget **no se dibuja**. Hay que reemplazarla por la clave real del dominio:

```bash
grep -rl 'data-sitekey="pagina pernostock"' --include=*.html .
```

y sustituirla por la clave provista por Google reCAPTCHA v3.

### 2. Los formularios envían a un endpoint del servidor

Los formularios apuntan a `/pub/casos-forms/formulario.php`, que **no existe en
este repositorio**: es un endpoint del servidor de producción. En local el
formulario se ve y se valida, pero al enviar devuelve 404.

Para probarlos de verdad hace falta o bien ese PHP en el hosting, o un endpoint
de pruebas propio.

### 3. `preguntas_frecuentes.html` y `sugerencias.html` están sin contenido

Ambas páginas muestran un aviso de "en construcción". Es el estado original del
proyecto, no un error: falta escribir el contenido.

### 4. El catálogo general vive en el servidor de producción

El botón "Descarga nuestro Catálogo" y dos fichas
(`nueva-ficha-tecnica-golilla-reparticion.pdf` y
`catalogo-estructural-baja.pdf`) apuntan a `https://pernostock.cl/...` porque
esos archivos no están en este repositorio. Si se agregan a
`media/pdf/fichas-tecnicas/`, se pueden enlazar localmente con:

```bash
python3 tools/fix_fichas_links.py
```

### 5. Los CSS están duplicados

Cada página carga su propia hoja de estilos en `css/archivos/`, y casi todas son
copias del mismo bloque de ~7 KB con pequeñas diferencias. Funciona, pero
cualquier cambio de estilo hay que replicarlo en varios archivos. Extraer un
`css/base.css` común sería el siguiente paso lógico.

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
