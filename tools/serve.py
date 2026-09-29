#!/usr/bin/env python3
"""Servidor local para previsualizar el sitio.

Uso:
    python3 tools/serve.py            # http://localhost:8000
    python3 tools/serve.py 8080       # otro puerto

No requiere dependencias externas ni PHP: el sitio es HTML estatico.
"""
import functools
import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Atende cada peticion en su propio hilo.

    El navegador abre varias conexiones a la vez (imagenes, CSS, JS); con un
    servidor de un solo hilo la pagina se queda esperando y las pruebas
    automatizadas expiran.
    """

    daemon_threads = True
    allow_reuse_address = True


class Handler(http.server.SimpleHTTPRequestHandler):
    """Sirve el sitio y muestra 404.html cuando el archivo no existe."""

    def translate_path(self, path: str) -> str:
        translated = super().translate_path(path)
        target = Path(translated)

        # Si no existe y no es una ruta de archivo con extension, prueba index.html
        if not target.exists() and not target.suffix:
            candidate = target / "index.html"
            if candidate.exists():
                return str(candidate)
        return translated

    def send_error(self, code, message=None, explain=None):
        # Reemplaza el error 404 por la pagina del sitio.
        if code == 404:
            not_found = ROOT / "404.html"
            if not_found.exists():
                body = not_found.read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        super().send_error(code, message, explain)

    def end_headers(self):
        # Sin cache durante el desarrollo.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = functools.partial(Handler, directory=str(ROOT))

    with ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Servidor de Pernostock en http://localhost:{port}")
        print("Ctrl+C para detener.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")


if __name__ == "__main__":
    main()
