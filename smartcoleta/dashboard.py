from __future__ import annotations

from .config import LOT_OPTIONS, MONTHS_SHORT, REGION_TO_LOT, TOOLTIP_LOT_REGIONS
from .filters import (
    cost_title,
    equipment_for_region,
    filter_cost_scope,
    filter_cost_type,
    filter_period,
    filter_scope,
    filter_type,
    lot_region_tooltips,
    period_label,
    population_for_scope,
    represented_regions,
    top_pairs,
)
from .formatters import br_currency, br_number, format_tons
from .models import ChartTooltip, DashboardModel, MetricDetailRow, Selection, SourceData


def build_dashboard_model(selection: Selection, source: SourceData) -> DashboardModel:
    volume = source.monthly[source.monthly["is_volume"]].copy()
    period_volume = filter_period(volume, selection)
    period_volume = filter_type(period_volume, selection.collection_type)
    period_volume = filter_scope(period_volume, selection)

    regional_period = filter_period(source.regional_volume, selection)
    regional_period = filter_type(regional_period, selection.collection_type)
    regional_period = filter_scope(regional_period, selection)
    regional_rows = regional_period[regional_period["regiao"].ne("")]
    lot_rows = regional_period[regional_period["regiao"].eq("") & regional_period["lote"].ne("")]

    cost_period = filter_period(source.costs, selection)
    cost_period = filter_cost_type(cost_period, selection.collection_type)
    cost_period = filter_cost_scope(cost_period, selection)
    cost_chart_title = cost_title(selection.collection_type)

    equipment = equipment_for_region(source, selection)
    monitored_regions = represented_regions(regional_period)
    regions_monitored = int(monitored_regions["regiao"].nunique())
    equipment_breakdown = [
        (str(label), int(count))
        for label, count in equipment["tipo_equipamento"].value_counts().items()
    ]
    region_counts = monitored_regions.groupby("lote")["regiao"].nunique()
    region_breakdown: list[MetricDetailRow] = []
    for lot in LOT_OPTIONS:
        if lot == "Todos":
            continue
        lot_count = int(region_counts.get(lot, 0))
        if lot_count <= 0:
            continue
        region_breakdown.append((lot, lot_count, 0))
        region_breakdown.append((", ".join(TOOLTIP_LOT_REGIONS[lot]), None, 1))

    volume_chart_tooltips: dict[str, ChartTooltip] = {}
    if selection.region != "Todas":
        volume_chart_data = top_pairs(regional_period.groupby("grupo_coleta")["valor"].sum(), limit=6)
        volume_chart_title = f"Volume por tipo em {selection.region}"
    elif selection.lot != "Todos" and lot_rows.empty:
        volume_chart_data = top_pairs(regional_rows.groupby("regiao")["valor"].sum(), limit=6)
        volume_chart_title = f"Volume por região no {selection.lot}"
    elif selection.lot != "Todos":
        volume_chart_data = top_pairs(regional_period.groupby("categoria")["valor"].sum(), limit=6)
        volume_chart_title = f"Volume por categoria no {selection.lot}"
        volume_chart_tooltips = lot_region_tooltips(volume_chart_data, selection.lot)
    else:
        volume_chart_data = top_pairs(regional_period.groupby("lote")["valor"].sum(), limit=6)
        volume_chart_title = "Volume por lote"
        volume_chart_tooltips = lot_region_tooltips(volume_chart_data)

    if not volume_chart_data:
        category_period = filter_type(filter_period(volume, selection), selection.collection_type)
        category_period = filter_scope(category_period, selection)
        volume_chart_data = top_pairs(category_period.groupby("categoria")["valor"].sum(), limit=6)
        volume_chart_title = "Volume por categoria"
        volume_chart_tooltips = lot_region_tooltips(
            volume_chart_data,
            selection.lot if selection.lot != "Todos" else None,
        )

    monthly_base = filter_period(volume, selection, include_month=False)
    monthly_base = filter_type(monthly_base, selection.collection_type)
    monthly_base = filter_scope(monthly_base, selection)
    if selection.year is None:
        monthly_totals = monthly_base.groupby("ano")["valor"].sum()
        monthly_volume = [(str(int(year)), float(value)) for year, value in monthly_totals.sort_index().items()]
        monthly_chart_title = "Volume anual"
    else:
        monthly_totals = monthly_base.groupby("mes")["valor"].sum()
        monthly_volume = [(MONTHS_SHORT[month], float(monthly_totals.get(month, 0))) for month in range(1, 13)]
        monthly_chart_title = f"Volume mensal em {selection.year}"

    cost_chart_data = top_pairs(cost_period.groupby("categoria")["valor"].sum(), limit=5)

    breakdown_series = period_volume.groupby("grupo_coleta")["valor"].sum().sort_values(ascending=False)
    collection_breakdown = [(str(label), float(value)) for label, value in breakdown_series.items()]

    if not regional_rows.empty and lot_rows.empty:
        ranking = top_pairs(regional_rows.groupby("regiao")["valor"].sum(), limit=5)
        ranking_title = "Ranking das regiões com maior volume"
        ranking_context = "Baseado no tipo de coleta selecionado"
    else:
        ranking = top_pairs(regional_period[regional_period["lote"].ne("")].groupby("lote")["valor"].sum(), limit=5)
        ranking_title = "Ranking dos lotes com maior volume"
        ranking_context = "Baseado nas categorias da base filtrada"

    summary_location = selection.region if selection.region != "Todas" else (ranking[0][0] if ranking else "Sem localidade disponível")
    if summary_location in LOT_OPTIONS:
        summary_region = "Todas"
        summary_lot = summary_location
    else:
        summary_region = summary_location
        summary_lot = REGION_TO_LOT.get(summary_region, selection.lot if selection.lot != "Todos" else "Sem lote")
    summary_selection = Selection(
        year=selection.year,
        month=selection.month,
        lot=summary_lot if summary_lot in LOT_OPTIONS else "Todos",
        region=summary_region if summary_region in source.regions else "Todas",
        collection_type=selection.collection_type,
    )
    summary_period = filter_type(filter_period(volume, summary_selection), summary_selection.collection_type)
    summary_period = filter_scope(summary_period, summary_selection)
    summary_year = filter_type(filter_period(volume, summary_selection, include_month=False), summary_selection.collection_type)
    summary_year = filter_scope(summary_year, summary_selection)
    summary_equipment = equipment_for_region(source, summary_selection)
    population_year = selection.year if selection.year is not None else int(source.population["ano"].dropna().astype(int).max())
    population = population_for_scope(source, summary_region, summary_lot, population_year)
    top_equipment = summary_equipment["tipo_equipamento"].value_counts()
    top_equipment_label = top_equipment.index[0] if not top_equipment.empty else "Sem dados"

    total_volume = float(period_volume["valor"].sum())
    total_cost = float(cost_period["valor"].sum())
    total_cost_label = br_currency(total_cost) if not cost_period.empty else "Sem dados"

    metrics = [
        ("Volume total", format_tons(total_volume), "▥", "green", None),
        ("Pontos de coleta", br_number(float(len(equipment))), "⌖", "blue", ("Pontos por tipo", [(label, count, 0) for label, count in equipment_breakdown], "Sem pontos por tipo")),
        ("Regiões monitoradas", br_number(float(regions_monitored)), "↗", "green", ("Regiões por lote", region_breakdown, "Sem regiões monitoradas")),
        (cost_chart_title, total_cost_label, "$", "blue", None),
    ]

    summary = [
        ("Localidade", summary_location),
        ("Lote operacional", summary_lot),
        ("Período", period_label(selection)),
        ("Volume no período", format_tons(float(summary_period["valor"].sum()))),
        ("Volume no ano", format_tons(float(summary_year["valor"].sum()))),
        ("Pontos de coleta", br_number(float(len(summary_equipment)))),
        ("População", br_number(population) if population is not None else "Sem dados"),
        ("Equipamento predominante", str(top_equipment_label)),
    ]

    return DashboardModel(
        source=source,
        selection=selection,
        metrics=metrics,
        volume_chart_title=volume_chart_title,
        volume_chart_data=volume_chart_data,
        volume_chart_tooltips=volume_chart_tooltips,
        monthly_volume=monthly_volume,
        monthly_chart_title=monthly_chart_title,
        cost_chart_title=cost_chart_title,
        cost_chart_data=cost_chart_data,
        collection_breakdown=collection_breakdown,
        ranking_title=ranking_title,
        ranking_context=ranking_context,
        ranking=ranking,
        summary=summary,
        period_label=period_label(selection),
    )
