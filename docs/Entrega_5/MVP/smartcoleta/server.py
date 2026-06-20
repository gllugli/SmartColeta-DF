from __future__ import annotations

import argparse
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .config import DATA_PATH, STATIC_DIR
from .templates import render_dashboard, render_error_page


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path in {"/", "/index.html", "/api/dashboard", "/api/dashboard/"}:
            try:
                self._send_html(render_dashboard(parse_qs(parsed.query)))
            except Exception as error:  # noqa: BLE001 - page should show data loading failures.
                self._send_html(render_error_page(error), status=500)
            return

        if parsed.path == "/static/dashboard.css":
            self._send_static_file(STATIC_DIR / "dashboard.css", "text/css; charset=utf-8")
            return

        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        self.send_error(404, "Página não encontrada")

    def _send_html(self, body: str, status: int = 200) -> None:
        self._send_bytes(body.encode("utf-8"), "text/html; charset=utf-8", status)

    def _send_static_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404, "Arquivo estático não encontrado")
            return
        self._send_bytes(path.read_bytes(), content_type)

    def _send_bytes(self, payload: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dashboard dinâmico do SmartColeta-DF.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", default=int(os.environ.get("PORT", "8000")), type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"SmartColeta-DF rodando em http://{args.host}:{args.port}")
    print(f"Base carregada de {DATA_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()
