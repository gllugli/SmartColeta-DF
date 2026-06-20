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

    do_GET = DashboardHandler.do_GET
    _send_html = DashboardHandler._send_html
    _send_static_file = DashboardHandler._send_static_file
    _send_bytes = DashboardHandler._send_bytes
    log_message = DashboardHandler.log_message
