from __future__ import annotations

import pandas as pd

from .config import LOT_OPTIONS, LOT_REGIONS, MONTHS, REGION_TO_LOT, TOOLTIP_LOT_REGIONS, TYPE_TO_INDICATORS
from .domain import lot_from_region
from .models import ChartTooltip, Selection, SourceData


def parse_int(value: str | None) -> int | None:
    if value in {None, "", "all", "Todos"}:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def first_query_value(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    if not values:
        return None
    return values[0]


def parse_selection(params: dict[str, list[str]], source: SourceData) -> Selection:
    raw_year = first_query_value(params, "ano")
    year = parse_int(raw_year)
    if raw_year not in {None, "", "Todos", "all"} and year not in source.years:
        year = max(source.years)

    raw_month = first_query_value(params, "mes")
    month = parse_int(raw_month)
    if raw_month not in {None, "", "Todos", "all"}:
        month_scope = source.monthly
        if year is not None:
            month_scope = month_scope[month_scope["ano"].eq(year)]
        months_available = month_scope["mes"].dropna().astype(int).unique().tolist()
        if month not in months_available:
            month = max(months_available) if months_available else None

    lot = first_query_value(params, "lote") or "Todos"
    if lot not in LOT_OPTIONS:
        lot = "Todos"

    region = first_query_value(params, "regiao") or "Todas"
    if region != "Todas" and region not in source.regions:
        region = "Todas"
    if lot != "Todos" and region != "Todas" and REGION_TO_LOT.get(region) != lot:
        region = "Todas"

    collection_type = first_query_value(params, "tipo") or "Todas"
    if collection_type != "Todas" and collection_type not in TYPE_TO_INDICATORS:
        collection_type = "Todas"

    return Selection(year=year, month=month, lot=lot, region=region, collection_type=collection_type)


def filter_period(df: pd.DataFrame, selection: Selection, include_month: bool = True) -> pd.DataFrame:
    filtered = df
    if selection.year is not None:
        filtered = filtered[filtered["ano"].eq(selection.year)]
    if include_month and selection.month is not None:
        filtered = filtered[filtered["mes"].eq(selection.month)]
    return filtered


def filter_type(df: pd.DataFrame, collection_type: str) -> pd.DataFrame:
    if collection_type == "Todas":
        return df
    indicators = TYPE_TO_INDICATORS.get(collection_type, [])
    return df[df["indicador"].isin(indicators)]


def filter_cost_type(df: pd.DataFrame, collection_type: str) -> pd.DataFrame:
    if collection_type == "Todas":
        return df
    if "grupo_coleta" not in df.columns:
        return df.iloc[0:0]
    return df[df["grupo_coleta"].eq(collection_type)]


def filter_cost_scope(df: pd.DataFrame, selection: Selection) -> pd.DataFrame:
    if "lote" not in df.columns:
        return df

    lot = selection.lot
    if selection.region != "Todas":
        lot = REGION_TO_LOT.get(selection.region, lot)
    if lot == "Todos":
        return df

    lot_rows = df[df["lote"].eq(lot)]
    global_rows = df[df["lote"].eq("")]
    return pd.concat([lot_rows, global_rows], ignore_index=False)


def filter_lot(df: pd.DataFrame, lot: str) -> pd.DataFrame:
    if lot == "Todos" or "lote" not in df.columns:
        return df
    return df[df["lote"].eq(lot)]


def filter_region(df: pd.DataFrame, region: str) -> pd.DataFrame:
    if region == "Todas" or "regiao" not in df.columns:
        return df
    return df[df["regiao"].eq(region)]


def filter_scope(df: pd.DataFrame, selection: Selection) -> pd.DataFrame:
    scoped = filter_lot(df, selection.lot)
    if selection.region == "Todas":
        return scoped

    region_lot = REGION_TO_LOT.get(selection.region, "")
    regional_rows = scoped[scoped["regiao"].eq(selection.region)] if "regiao" in scoped.columns else scoped.iloc[0:0]
    lot_rows = scoped[
        scoped["regiao"].eq("")
        & scoped["lote"].eq(region_lot)
    ] if {"regiao", "lote"}.issubset(scoped.columns) else scoped.iloc[0:0]
    return pd.concat([regional_rows, lot_rows], ignore_index=False)


def represented_regions(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[tuple[str, str]] = []
    if not {"regiao", "lote"}.issubset(df.columns):
        return pd.DataFrame(rows, columns=["regiao", "lote"])

    for regiao, lote in df[["regiao", "lote"]].drop_duplicates().itertuples(index=False, name=None):
        if regiao:
            rows.append((str(regiao), str(lote) if lote else lot_from_region(regiao)))
            continue
        if lote in LOT_REGIONS:
            rows.extend((region, str(lote)) for region in LOT_REGIONS[str(lote)])

    return pd.DataFrame(rows, columns=["regiao", "lote"]).drop_duplicates()


def top_pairs(series: pd.Series, limit: int = 6) -> list[tuple[str, float]]:
    if series.empty:
        return []
    return [(str(label), float(value)) for label, value in series.sort_values(ascending=False).head(limit).items()]


def lot_region_tooltips(
    data: list[tuple[str, float]],
    fallback_lot: str | None = None,
) -> dict[str, ChartTooltip]:
    tooltips: dict[str, ChartTooltip] = {}
    for label, _ in data:
        lot = label if label in TOOLTIP_LOT_REGIONS else fallback_lot
        if lot in TOOLTIP_LOT_REGIONS:
            tooltips[label] = (f"Regiões no {lot}", TOOLTIP_LOT_REGIONS[lot])
    return tooltips


def period_label(selection: Selection) -> str:
    if selection.year is None and selection.month is None:
        return "Todos os períodos"
    if selection.year is None:
        return f"{MONTHS[selection.month]} de todos os anos"
    if selection.month is None:
        return f"Todos os meses/{selection.year}"
    return f"{MONTHS[selection.month]}/{selection.year}"


def cost_title(collection_type: str) -> str:
    if collection_type == "Todas":
        return "Custo operacional"
    return f"Custo operacional {collection_type}"


def equipment_for_region(source: SourceData, selection: Selection) -> pd.DataFrame:
    latest_equipment_year = source.equipment["ano"].dropna().astype(int).max()
    equipment = source.equipment[source.equipment["ano"].eq(latest_equipment_year)]
    equipment = filter_lot(equipment, selection.lot)
    return filter_region(equipment, selection.region)


def population_for_region(source: SourceData, region: str, year: int) -> float | None:
    population = source.population[source.population["regiao"].eq(region)]
    if population.empty:
        return None
    if year in population["ano"].dropna().astype(int).tolist():
        row = population[population["ano"].eq(year)].tail(1)
    else:
        row = population.sort_values("ano").tail(1)
    if row.empty:
        return None
    return float(row["pop_total"].iloc[0])


def population_for_scope(source: SourceData, region: str, lot: str, year: int) -> float | None:
    if region != "Todas":
        return population_for_region(source, region, year)
    if lot not in LOT_OPTIONS[1:]:
        return None

    population = source.population[
        source.population["lote"].eq(lot)
        & source.population["regiao"].ne("Total")
    ]
    if population.empty:
        return None

    years = population["ano"].dropna().astype(int)
    target_year = year if year in years.tolist() else int(years.max())
    scoped = population[population["ano"].eq(target_year)]
    if scoped.empty:
        return None
    return float(scoped["pop_total"].sum())
