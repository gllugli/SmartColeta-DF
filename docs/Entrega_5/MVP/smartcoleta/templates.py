from __future__ import annotations

from typing import Iterable

from .charts import collection_progress, metric_card, svg_bar_chart, svg_horizontal_bars, svg_line_chart
from .config import DATA_PATH, LOT_OPTIONS, MONTHS, TYPE_TO_INDICATORS
from .dashboard import build_dashboard_model
from .data_loader import get_source_data
from .filters import parse_selection
from .formatters import attr, format_tons, text


def option_list(options: Iterable[tuple[str, str]], selected: str) -> str:
    return "".join(
        f'<option value="{attr(value)}"{" selected" if value == selected else ""}>{text(label)}</option>'
        for value, label in options
    )


def render_dashboard(params: dict[str, list[str]] | None = None) -> str:
    params = params or {}
    source = get_source_data()
    selection = parse_selection(params, source)
    model = build_dashboard_model(selection, source)

    selected_year = str(selection.year) if selection.year is not None else "Todos"
    selected_month = str(selection.month) if selection.month is not None else "Todos"
    year_options = [("Todos", "Todos")] + [(str(year), str(year)) for year in sorted(source.years, reverse=True)]
    month_options = [("Todos", "Todos")] + [(str(month), MONTHS[month]) for month in range(1, 13)]
    lot_options = [(lot, lot) for lot in LOT_OPTIONS]
    type_options = [("Todas", "Todas")] + [(value, value) for value in TYPE_TO_INDICATORS]

    ranking_rows = "".join(
        f"""
        <div class="ranking-row">
            <strong>{index}º</strong>
            <span>{text(region)}</span>
            <em>{text(format_tons(value))}</em>
        </div>
        """
        for index, (region, value) in enumerate(model.ranking, start=1)
    ) or '<div class="empty-row">Sem dados para o ranking atual.</div>'

    summary_rows = "".join(
        f"""
        <div class="summary-row">
            <span>{text(label)}:</span>
            <strong>{text(value)}</strong>
        </div>
        """
        for label, value in model.summary
    )

    metric_html = "".join(metric_card(*metric) for metric in model.metrics)

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SmartColeta-DF | Dashboard</title>
    <link rel="stylesheet" href="/static/dashboard.css">
</head>
<body>
    <main class="page">
        <section class="panel header">
            <div>
                <h1>SmartColeta - DF</h1>
                <p>Dashboard de Apoio à Tomada de Decisões</p>
            </div>
            <button class="primary-action" type="submit" form="filters-form">Atualizar Dados</button>
        </section>

        <form id="filters-form" class="panel filters" method="get" aria-label="Filtros do dashboard">
            <div class="field">
                <label for="ano">Ano</label>
                <select id="ano" name="ano">{option_list(year_options, selected_year)}</select>
            </div>
            <div class="field">
                <label for="mes">Mês</label>
                <select id="mes" name="mes">{option_list(month_options, selected_month)}</select>
            </div>
            <div class="field">
                <label for="lote">Lote</label>
                <select id="lote" name="lote">{option_list(lot_options, selection.lot)}</select>
            </div>
            <div class="field">
                <label for="tipo">Tipo de Coleta</label>
                <select id="tipo" name="tipo">{option_list(type_options, selection.collection_type)}</select>
            </div>
        </form>

        <section class="metrics" aria-label="Indicadores principais">
            {metric_html}
        </section>

        <section class="grid" aria-label="Gráficos principais">
            <article class="content-card">
                <h2>{text(model.volume_chart_title)}</h2>
                <span class="card-context">Dados filtrados por {text(model.period_label)}</span>
                {svg_bar_chart(model.volume_chart_data, model.volume_chart_title, model.volume_chart_tooltips)}
            </article>
            <article class="content-card">
                <h2>{text(model.monthly_chart_title)}</h2>
                <span class="card-context">Série anual conforme filtros de lote e tipo</span>
                {svg_line_chart(model.monthly_volume)}
            </article>
            <article class="content-card">
                <h2>{text(model.cost_chart_title)}</h2>
                {svg_horizontal_bars(model.cost_chart_data, f"{model.cost_chart_title} por categoria")}
            </article>
            <article class="content-card">
                <h2>Distribuição por tipo de coleta</h2>
                <span class="card-context">Somatório em toneladas no período filtrado</span>
                <div class="progress-list">
                    {collection_progress(model.collection_breakdown)}
                </div>
            </article>
        </section>

        <section class="grid" aria-label="Tabelas e resumo">
            <article class="content-card tall">
                <h2>{text(model.ranking_title)}</h2>
                <span class="card-context">{text(model.ranking_context)}</span>
                <div class="ranking">
                    {ranking_rows}
                </div>
            </article>
            <article class="content-card tall">
                <h2>Resumo da localidade líder</h2>
                <span class="card-context">A localidade líder respeita os filtros de lote, ano, mês e tipo</span>
                <div class="summary">
                    {summary_rows}
                </div>
            </article>
        </section>
    </main>
</body>
</html>"""


def render_error_page(error: Exception) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>SmartColeta-DF | Erro</title>
    <style>
        body {{
            margin: 0;
            background: #f6f7f9;
            color: #0f2442;
            font-family: "Segoe UI", Arial, sans-serif;
        }}
        main {{
            max-width: 860px;
            margin: 60px auto;
            background: #fff;
            border: 1px solid #e3e8ef;
            border-radius: 10px;
            padding: 28px;
            box-shadow: 0 1px 2px rgba(15, 36, 66, 0.08);
        }}
        code {{
            display: block;
            margin-top: 16px;
            padding: 14px;
            background: #f1f5f9;
            border-radius: 7px;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <main>
        <h1>Não foi possível carregar o dashboard</h1>
        <p>Verifique se a planilha tratada existe em <strong>{text(DATA_PATH)}</strong> e se as dependências estão instaladas.</p>
        <code>{text(type(error).__name__)}: {text(error)}</code>
    </main>
</body>
</html>"""
