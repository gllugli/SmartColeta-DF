from __future__ import annotations

import math

from .formatters import attr, br_currency, br_number, format_tons, text
from .models import ChartTooltip, MetricDetails


def nice_upper(value: float) -> float:
    if value <= 0:
        return 1

    exponent = math.floor(math.log10(value))
    base = 10**exponent
    fraction = value / base
    if fraction <= 1:
        nice = 1
    elif fraction <= 2:
        nice = 2
    elif fraction <= 5:
        nice = 5
    else:
        nice = 10
    return nice * base


def chart_ticks(max_value: float, count: int = 5) -> list[float]:
    upper = nice_upper(max_value)
    return [upper * index / (count - 1) for index in range(count)]


def svg_empty_state(label: str) -> str:
    return f"""
    <div class="empty-state">
        <strong>{text(label)}</strong>
        <span>Altere os filtros para visualizar outra combinação de dados.</span>
    </div>
    """


def wrapped_region_lines(regions: list[str], max_chars: int = 34) -> list[str]:
    lines: list[str] = []
    current = ""
    for region in regions:
        addition = region if not current else f", {region}"
        if current and len(current) + len(addition) > max_chars:
            lines.append(current)
            current = region
        else:
            current += addition
    if current:
        lines.append(current)
    return lines


def svg_chart_tooltip(
    x_center: float,
    bar_y: float,
    title: str,
    regions: list[str],
    left_limit: float,
    right_limit: float,
) -> str:
    lines = wrapped_region_lines(regions)
    tooltip_w = 270
    line_h = 14
    tooltip_h = 38 + line_h * len(lines)
    tooltip_x = min(max(x_center - tooltip_w / 2, left_limit), right_limit - tooltip_w)
    tooltip_y = max(8, bar_y - tooltip_h - 10)

    text_lines = [
        f'<text class="chart-tooltip-title" x="{tooltip_x + 14:.1f}" y="{tooltip_y + 20:.1f}">{text(title)}</text>'
    ]
    for index, line in enumerate(lines):
        text_lines.append(
            f'<text class="chart-tooltip-text" x="{tooltip_x + 14:.1f}" y="{tooltip_y + 40 + index * line_h:.1f}">{text(line)}</text>'
        )

    return f"""
        <g class="chart-tooltip" aria-hidden="true">
            <rect class="chart-tooltip-panel" x="{tooltip_x:.1f}" y="{tooltip_y:.1f}" width="{tooltip_w}" height="{tooltip_h:.1f}" rx="8" />
            {''.join(text_lines)}
        </g>
    """


def svg_bar_chart(
    data: list[tuple[str, float]],
    aria_label: str,
    tooltips: dict[str, ChartTooltip] | None = None,
) -> str:
    if not data:
        return svg_empty_state("Sem dados para este gráfico")

    tooltips = tooltips or {}
    width, height = 760, 300
    left, right, top, bottom = 70, 18, 20, 54
    chart_w = width - left - right
    chart_h = height - top - bottom
    max_y = nice_upper(max(value for _, value in data))
    ticks = chart_ticks(max_y)
    gap = 24 if len(data) > 5 else 32
    bar_w = max(20, (chart_w - gap * (len(data) - 1)) / len(data))

    pieces: list[str] = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{attr(aria_label)}">',
    ]

    for tick in ticks:
        y = top + chart_h - (tick / max_y) * chart_h
        pieces.append(f'<line class="grid-line" x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" />')
        pieces.append(f'<text class="axis-label" x="{left - 10}" y="{y + 4:.1f}" text-anchor="end">{text(br_number(tick))}</text>')

    pieces.append(f'<line class="axis-line" x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" />')
    pieces.append(f'<line class="axis-line" x1="{left}" y1="{top + chart_h}" x2="{width - right}" y2="{top + chart_h}" />')

    for index, (label, value) in enumerate(data):
        x = left + index * (bar_w + gap)
        bar_h = (value / max_y) * chart_h if max_y else 0
        y = top + chart_h - bar_h
        short_label = label if len(label) <= 16 else f"{label[:14]}..."
        tooltip = tooltips.get(label)
        group_class = "chart-bar-group has-chart-tooltip" if tooltip else "chart-bar-group"
        focus_attr = ""
        if tooltip:
            tooltip_title, regions = tooltip
            region_label = ", ".join(regions)
            bar_aria = f"{label}: {br_number(value)}. {tooltip_title}: {region_label}"
            focus_attr = f' tabindex="0" role="img" aria-label="{attr(bar_aria)}"'
        pieces.append(f'<g class="{group_class}"{focus_attr}>')
        pieces.append(f'<rect class="bar" x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" rx="4" />')
        if tooltip:
            pieces.append(f'<rect class="chart-bar-hit" x="{x:.1f}" y="{top}" width="{bar_w:.1f}" height="{chart_h}" />')
        pieces.append(f'<text class="axis-label" x="{x + bar_w / 2:.1f}" y="{top + chart_h + 24}" text-anchor="middle">{text(short_label)}</text>')
        pieces.append(f'<text class="value-label" x="{x + bar_w / 2:.1f}" y="{max(y - 7, 12):.1f}" text-anchor="middle">{text(br_number(value))}</text>')
        if tooltip:
            pieces.append(svg_chart_tooltip(x + bar_w / 2, y, tooltip_title, regions, left, width - right))
        pieces.append("</g>")

    pieces.append("</svg>")
    return "".join(pieces)


def svg_line_chart(data: list[tuple[str, float]]) -> str:
    if not data:
        return svg_empty_state("Sem dados para este gráfico")

    width, height = 760, 300
    left, right, top, bottom = 70, 18, 20, 48
    chart_w = width - left - right
    chart_h = height - top - bottom
    max_y = nice_upper(max(value for _, value in data))
    ticks = chart_ticks(max_y)
    step = chart_w / max(len(data) - 1, 1)

    def point(index: int, value: float) -> tuple[float, float]:
        x = left + index * step
        y = top + chart_h - (value / max_y) * chart_h if max_y else top + chart_h
        return x, y

    points = [point(index, value) for index, (_, value) in enumerate(data)]
    point_attr = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)

    pieces: list[str] = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Volume de lixo por mês">',
    ]

    for tick in ticks:
        y = top + chart_h - (tick / max_y) * chart_h
        pieces.append(f'<line class="grid-line" x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" />')
        pieces.append(f'<text class="axis-label" x="{left - 10}" y="{y + 4:.1f}" text-anchor="end">{text(br_number(tick))}</text>')

    for index, (label, _) in enumerate(data):
        x = left + index * step
        pieces.append(f'<line class="grid-line" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + chart_h}" />')
        pieces.append(f'<text class="axis-label" x="{x:.1f}" y="{top + chart_h + 24}" text-anchor="middle">{text(label)}</text>')

    pieces.append(f'<line class="axis-line" x1="{left}" y1="{top}" x2="{left}" y2="{top + chart_h}" />')
    pieces.append(f'<line class="axis-line" x1="{left}" y1="{top + chart_h}" x2="{width - right}" y2="{top + chart_h}" />')
    pieces.append(f'<polyline class="trend-line" points="{point_attr}" />')

    for x, y in points:
        pieces.append(f'<circle class="trend-point" cx="{x:.1f}" cy="{y:.1f}" r="5" />')

    pieces.append("</svg>")
    return "".join(pieces)


def svg_horizontal_bars(data: list[tuple[str, float]], aria_label: str = "Custo operacional por categoria") -> str:
    if not data:
        return svg_empty_state("Sem dados para este gráfico")

    width, height = 760, 300
    left, right, top = 250, 120, 28
    row_h = 46
    bar_h = 18
    max_value = max(value for _, value in data)
    chart_w = width - left - right

    pieces = [
        f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="{attr(aria_label)}">',
    ]

    for index, (label, value) in enumerate(data):
        y = top + index * row_h
        bar_w = (value / max_value) * chart_w if max_value else 0
        short_label = label if len(label) <= 34 else f"{label[:32]}..."
        pieces.append(f'<text class="axis-label strong-label" x="{left - 14}" y="{y + 15}" text-anchor="end">{text(short_label)}</text>')
        pieces.append(f'<rect class="bar-bg" x="{left}" y="{y}" width="{chart_w}" height="{bar_h}" rx="9" />')
        pieces.append(f'<rect class="bar bar-blue" x="{left}" y="{y}" width="{bar_w:.1f}" height="{bar_h}" rx="9" />')
        pieces.append(f'<text class="axis-label" x="{left + chart_w + 12}" y="{y + 15}">{text(br_currency(value))}</text>')

    pieces.append("</svg>")
    return "".join(pieces)


def collection_progress(items: list[tuple[str, float]]) -> str:
    if not items:
        return svg_empty_state("Sem dados para esta combinação de filtros")

    total = sum(value for _, value in items)
    rows = []
    for label, value in items:
        percent = value / total * 100 if total else 0
        rows.append(
            f"""
            <div class="progress-row">
                <div class="progress-head">
                    <span>{text(label)}</span>
                    <strong>{text(format_tons(value))}</strong>
                </div>
                <div class="progress-track">
                    <span style="width: {percent:.1f}%"></span>
                </div>
            </div>
            """
        )
    return "".join(rows)


def metric_card(
    label: str,
    value: str,
    icon: str,
    accent: str,
    details: MetricDetails | None = None,
) -> str:
    tooltip = ""
    card_class = "metric-card"
    focus_attr = ""
    if details is not None:
        tooltip_title, detail_rows, empty_message = details
        card_class += " has-tooltip"
        focus_attr = ' tabindex="0"'
        tooltip_rows = []
        for detail_label, count, level in detail_rows:
            row_class = "metric-tooltip-row"
            if level > 0:
                row_class += " is-nested"
            count_html = "" if count is None else f"<strong>{text(br_number(float(count)))}</strong>"
            tooltip_rows.append(
                f"""
                <div class="{row_class}">
                    <span>{text(detail_label)}</span>
                    {count_html}
                </div>
                """
            )
        rows = "".join(tooltip_rows)
        if not rows:
            rows = f'<div class="metric-tooltip-empty">{text(empty_message)}</div>'
        tooltip = f"""
        <div class="metric-tooltip" role="tooltip">
            <span class="metric-tooltip-title">{text(tooltip_title)}</span>
            <div class="metric-tooltip-list">
                {rows}
            </div>
        </div>
        """

    return f"""
    <article class="{card_class}"{focus_attr}>
        <div class="metric-head">
            <span>{text(label)}</span>
            <span class="metric-icon {attr(accent)}">{text(icon)}</span>
        </div>
        <strong>{text(value)}</strong>
        {tooltip}
    </article>
    """
