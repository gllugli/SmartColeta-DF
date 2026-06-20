from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MVP_DIR = PROJECT_ROOT / "docs" / "Entrega_5" / "MVP"

if str(MVP_DIR) not in sys.path:
    sys.path.insert(0, str(MVP_DIR))

from smartcoleta.server import DashboardHandler  # noqa: E402


class handler(DashboardHandler):
    """Vercel Python Function entrypoint."""

