from __future__ import annotations

from functools import lru_cache

import pandas as pd

from .config import (
    COST_LOT_BY_INDICATOR,
    DATA_PATH,
    LOT_OPTIONS,
    MONTHLY_COST_TYPE_BY_CATEGORY,
    PEV_COST_TYPE_BY_CATEGORY,
    REGION_TO_LOT,
)
from .domain import indicator_group, lot_from_category, lot_from_region, normalize_region_name
from .models import SourceData


def data_mtime() -> int:
    return int(DATA_PATH.stat().st_mtime)


@lru_cache(maxsize=4)
def load_source_data(_: int) -> SourceData:
    monthly = pd.read_excel(DATA_PATH, sheet_name="base_mensal_consolidada")
    pev_costs = pd.read_excel(DATA_PATH, sheet_name="custos_operacao_pev")
    equipment = pd.read_excel(DATA_PATH, sheet_name="equipamentos_por_ra")
    population = pd.read_excel(DATA_PATH, sheet_name="populacao_df")

    monthly["valor"] = pd.to_numeric(monthly["valor"], errors="coerce").fillna(0)
    monthly["ano"] = pd.to_numeric(monthly["ano"], errors="coerce").astype("Int64")
    monthly["mes"] = pd.to_numeric(monthly["mes"], errors="coerce").astype("Int64")
    monthly["grupo_coleta"] = monthly["indicador"].astype(str).map(indicator_group)
    monthly["is_volume"] = monthly["indicador"].astype(str).str.endswith("(t)")
    monthly["regiao"] = monthly["categoria"].map(normalize_region_name)
    monthly["regiao"] = monthly["regiao"].where(monthly["regiao"].isin(REGION_TO_LOT), "")
    monthly["lote"] = monthly["categoria"].map(lot_from_category)

    monthly_costs = monthly[
        monthly["indicador"].isin(COST_LOT_BY_INDICATOR)
        & monthly["categoria"].isin(MONTHLY_COST_TYPE_BY_CATEGORY)
    ].copy()
    monthly_costs["lote"] = monthly_costs["indicador"].map(COST_LOT_BY_INDICATOR)
    monthly_costs["grupo_coleta"] = monthly_costs["categoria"].map(MONTHLY_COST_TYPE_BY_CATEGORY)
    monthly_costs["regiao"] = ""

    regional_volume = monthly[
        monthly["is_volume"]
        & (
            monthly["regiao"].ne("")
            | monthly["lote"].isin(LOT_OPTIONS[1:])
        )
    ].copy()

    pev_costs["valor"] = pd.to_numeric(pev_costs["valor"], errors="coerce").fillna(0)
    pev_costs["ano"] = pd.to_numeric(pev_costs["ano"], errors="coerce").astype("Int64")
    pev_costs["mes"] = pd.to_numeric(pev_costs["mes"], errors="coerce").astype("Int64")
    pev_costs["indicador"] = pev_costs["secao"]
    pev_costs["grupo_coleta"] = pev_costs["categoria"].map(PEV_COST_TYPE_BY_CATEGORY)
    pev_costs["lote"] = ""
    pev_costs["regiao"] = ""
    pev_costs = pev_costs[pev_costs["grupo_coleta"].notna()].copy()

    cost_columns = [
        "aba_origem",
        "ano",
        "mes",
        "data_referencia",
        "indicador",
        "categoria",
        "valor",
        "grupo_coleta",
        "lote",
        "regiao",
    ]
    costs = pd.concat(
        [monthly_costs[cost_columns], pev_costs[cost_columns]],
        ignore_index=True,
    )

    equipment["ano"] = pd.to_numeric(equipment["ano"], errors="coerce").astype("Int64")
    equipment["regiao"] = equipment["regiao_administrativa"].map(normalize_region_name)
    equipment["tipo_equipamento"] = equipment["tipo_equipamento"].astype(str)
    equipment["lote"] = equipment["regiao"].map(lot_from_region)

    population["ano"] = pd.to_numeric(population["ano"], errors="coerce").astype("Int64")
    population["pop_total"] = pd.to_numeric(population["pop_total"], errors="coerce").fillna(0)
    population["regiao"] = population["regiao_administrativa"].map(normalize_region_name)
    population["lote"] = population["regiao"].map(lot_from_region)

    years = sorted(monthly["ano"].dropna().astype(int).unique().tolist())
    regions = sorted(
        set(regional_volume["regiao"].dropna().tolist())
        | set(equipment["regiao"].dropna().tolist())
        | set(population.loc[population["regiao"].ne("Total"), "regiao"].dropna().tolist())
    )

    return SourceData(
        monthly=monthly,
        regional_volume=regional_volume,
        costs=costs,
        equipment=equipment,
        population=population,
        years=years,
        regions=regions,
    )


def get_source_data() -> SourceData:
    return load_source_data(data_mtime())
