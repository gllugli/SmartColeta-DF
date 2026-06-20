from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MVP_DIR = PROJECT_ROOT / "docs" / "Entrega_5" / "MVP"

if str(MVP_DIR) not in sys.path:
    sys.path.insert(0, str(MVP_DIR))

from smartcoleta.server import DashboardHandler  # noqa: E402


class handler(BaseHTTPRequestHandler):
    """Vercel Python Function entrypoint."""

    def do_GET(self) -> None:
        DashboardHandler.do_GET(self)

    def _send_html(self, body: str, status: int = 200) -> None:
        DashboardHandler._send_html(self, body, status)

    def _send_static_file(self, path: Path, content_type: str) -> None:
        DashboardHandler._send_static_file(self, path, content_type)

    def _send_bytes(self, payload: bytes, content_type: str, status: int = 200) -> None:
        DashboardHandler._send_bytes(self, payload, content_type, status)

    def log_message(self, format: str, *args: object) -> None:
        DashboardHandler.log_message(self, format, *args)
