from __future__ import annotations

import html


def attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(value: object) -> str:
    return html.escape(str(value))


def br_number(value: float, decimals: int = 0) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def br_currency(value: float) -> str:
    return f"R$ {br_number(value, 2)}"


def format_tons(value: float) -> str:
    decimals = 1 if 0 < abs(value) < 100 else 0
    return f"{br_number(value, decimals)} t"
